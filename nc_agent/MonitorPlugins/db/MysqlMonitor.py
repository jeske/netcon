#!/neo/opt/bin/python --

## MysqlMonitor.py
##
## David Jeske <jeske@neotonic.com>
## 02-02-2004

'''
MysqlMonitor.py -- code for checking Mysql db status
'''  # '

import os,sys,string
import re
import MySQLdb


class MysqlMonitor:
    def __init__(self,ncc):
	self.ncc = ncc

    def collectData(self,config):

        if string.strip(config):
            # user%pass@host:db
            m = re.match("([^ ]+)%([^ ]*)@([^ ]+):([^ ]+)",config)
            if m:
                user = m.group(1)
                password = m.group(2)
                host = m.group(3)
                database = m.group(4)
            else:
                raise "Invalid config: %s" % config
      
        else: 
            host = "localhost"
            user = "root"
            password = ""
            database = "netcon"

# 'Uptime: 2431621  Threads: 3  Questions: 49794953  Slow queries: 98  Opens: 48  Flush tables: 1  Open tables: 42 Queries per second avg: 20.478'

        stat_name_map = {
            'Uptime' : ('uptime','total'),
            'Threads' : ('threads', 'cur'),
            'Questions' : ('queries', 'total'),
            'Slow queries' : ('slow_queries', 'total'),
            'Opens' : ('opens','total'),
            'Flush tables' : ('flush_tables', 'total'),
            'Open tables' : ('open_tables', 'cur'),
            'Queries per second avg' : ('queries_per_second','cur') 
          }

        db = MySQLdb.connect(host = host, user = user, passwd = password, db=database)
        status_line = db.stat()
        print "status_line = %s" % status_line
        status_line = re.sub("([0-9.]+)","\\1 |",status_line)
        status_pieces = string.split(status_line,"|")

        for piece in status_pieces:
            subparts = string.split(piece,":")
            if len(subparts) == 2:
                name = string.strip(subparts[0])
                try:
                    value = float(string.strip(subparts[1]))
                except ValueError:
                    print "unknown value in subparts: %s" % repr(subparts)
                    continue

                if stat_name_map.has_key(name):
                    statname,stattype = stat_name_map[name]
                    self.ncc.newData("mysql/%s:%s" % (statname,stattype),
                         '',float(value),hostname=host)

        # SubEnt name, state, mesg, data for log, trigger
        # self.setState('innodb0', state, mesg, '%s %s' % (self.free_amt, trigger['trigger']), trigger)


def makeMonitor(ncc):
    return MysqlMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a,**b):
            print string.join(map(lambda x:str(x),a)," ")
    mon = makeMonitor(DummyNCC())
    mon.collectData('')
    mon.collectData("root%@localhost:netcon")

if __name__ == "__main__":
    test()
