#!/neo/opt/bin/python
#
# This monitor attempts to parse the syslog output of postfix
# Loosely based on the rrd tool mailgraph.pl:
# http://people.ee.ethz.ch/~dws/software/mailgraph/

import os,sys,string, time
import re
import md5
import IncLogMonitor

class PostfixLogMonitor (IncLogMonitor.IncLogMonitor):
    def __init__ (self, ncc):
        IncLogMonitor.IncLogMonitor.__init__(self, ncc)
        # We define our own datafile since multiple log monitors might
        # watch the maillog
        self.datafile = "/tmp/netcon/postfix_log_monitor.data"

    def collectData(self, config):
        logfile = config

        # lines look like:
        # Aug 31 04:02:15 localhost postfix/smtpd[27536]: 02E3A2799B: client=c5.neotonic.com[66.7.159.75]
        # returns host, program, message
        logline_re = re.compile('\S+ \d+ \S+ (\S+) (\S+): (.*)')

        # FIXME: Later, we can actually understand the date format, and then
        # store that so we never process data in the past... mostly

        fp = self.reopen_file(logfile)
        lines = 0
        received = 0
        rejected = 0
        sent = 0
        bounced = 0
        bytes = 0
        while 1:
            line = fp.readline()
            if not line: break
            lines = lines + 1
            if line.find("postfix") == -1: continue
            m = logline_re.match(line)
            if m:
                (host, program, msg) = m.groups()
                if program[:13] == "postfix/smtpd":
                    if re.match('[0-9A-F]+: client=(\S+)', msg):
                        received = received + 1
                    elif re.match('([0-9A-F]+: )?reject: ', msg):
                        rejected = rejected + 1
                elif program[:12] == "postfix/smtp":
                    if msg.find(' status=sent ') != -1:
                        sent = sent + 1
                    elif msg.find(' status=bounced ') != -1:
                        bounced = bounced + 1
                elif program[:13] == "postfix/local":
                    if msg.find(' status=bounced ') != -1:
                        bounced = bounced + 1
                elif program[:15] == "postfix/cleanup":
                    if re.match('[0-9A-F]+: (?:reject|discard): ', msg):
                        rejected = rejected + 1
                elif program[:12] == "postfix/pipe":
                    if msg.find(' status=sent ') != -1:
                        sent = sent + 1
                    elif msg.find(' status=bounced ') != -1:
                        bounced = bounced + 1
                elif program[:12] == "postfix/qmgr":
                    sm = re.search(" size=(\d+)", msg)
                    if sm:
                        bytes = bytes + int(sm.group(1))
                
            #else:
            #    print "Unable to handle line %s" % line
            if lines % 1000 == 0:
                print "Processed %d lines" % lines

        self.close_file(logfile, fp)

	self.ncc.newData("maillog/received:inc",logfile,received)
	self.ncc.newData("maillog/sent:inc",logfile,sent)
	self.ncc.newData("maillog/rejected:inc",logfile,rejected)
	self.ncc.newData("maillog/bounced:inc",logfile,bounced)
	self.ncc.newData("maillog/kilobytes:inc",logfile,bytes / 1024.0)


def makeMonitor(ncc):
    return PostfixLogMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = PostfixLogMonitor(DummyNCC())
    mon.collectData('/var/log/maillog')
    # mon.collectData('maillog.2')

if __name__ == "__main__":
    test()
