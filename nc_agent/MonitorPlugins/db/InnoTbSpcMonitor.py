#!/neo/opt/bin/python --

## InnoTbSpcMonitor
##
## David Jeske <jeske@neotonic.com>
## 08-24-2003
## Brandon Long <blong@neotonic.com>
## 04-29-2002

'''
InnoTbSpcMonitor.py -- code for checking if we're getting low on innodb
                     table space in our mysql server.

'''  # '

import os,sys,string
import re
import MySQLdb


class InnoTbSpcMonitor:
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

        db = MySQLdb.connect(host = host, user = user, passwd = password, db=database)
        cursor = db.cursor()
        cursor.execute("show table status")
        rows = cursor.fetchall()
        free_re = re.compile("InnoDB free: ([0-9]+) kB")
        free_amt = 0
        for row in rows:
            # The InnoDB free is indicated in the comment field, column 15
            comment = row[14]
            m = free_re.search(comment)
            if m:
                free_amt = int(m.group(1))
                break
        print "InnoDB: Free space at %s kB" % free_amt
	self.ncc.newData("mysql/innodb/free:cur",database,free_amt,hostname=host)

        # SubEnt name, state, mesg, data for log, trigger
        # self.setState('innodb0', state, mesg, '%s %s' % (self.free_amt, trigger['trigger']), trigger)


def makeMonitor(ncc):
    return InnoTbSpcMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a,**b):
            print string.join(map(lambda x:str(x),a)," ")
    mon = InnoTbSpcMonitor(DummyNCC())
    mon.collectData('')
    mon.collectData("root%@localhost:netcon")

if __name__ == "__main__":
    test()
