#!/neo/opt/bin/python

# REQUIRES Python 2.0 or greater for md5.hexdigest()
# This is nearly identical to HTTPLogMonitor, except we have an extra parameter
# on the front of our log files (the virtual domain)

import os,sys,string, time
import re
import md5
import IncLogMonitor

class VHTTPLogMonitor (IncLogMonitor.IncLogMonitor):
    def collectData(self, config):
        logfile = config

        logline_re = re.compile('\S+ (\S+) \S+ \S+ \[[^\]]+\] "[^"]+" (\d+) (\d+|-)')

        fp = self.reopen_file(logfile)
        hits = 0
        errs = 0
        bytes = 0
        while 1:
            line = fp.readline()
            if not line: break
            hits = hits + 1
            m = logline_re.match(line)
            if m:
                status = int(m.group(2))
                try:
                    length = int(m.group(3))
                except ValueError:
                    length = 0
                bytes = bytes + length
                if status == 500:
                    errs = errs + 1
            #else:
            #    print "Unable to handle line %s" % line
            if hits % 1000 == 0:
                print "Processed %d lines" % hits

        self.close_file(logfile, fp)

	self.ncc.newData("weblog/hits:inc",logfile,hits)
	self.ncc.newData("weblog/errors:inc",logfile,errs)
	self.ncc.newData("weblog/kilobytes:inc",logfile,bytes / 1024.0)


def makeMonitor(ncc):
    return VHTTPLogMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = VHTTPLogMonitor(DummyNCC())
    mon.collectData('/neo/log/web_access.log')

if __name__ == "__main__":
    test()
