#!/usr/bin/python

import os,sys,string, time
import commands
import re

class ProcInfo:
    def __init__(self,pid,tty,stat,time,proc):
        self.pid = pid
        self.tty = tty
        self.stat = stat
        self.time = time
        self.proc = proc


class ProcMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

    def collectData(self,config):
	pl = self.getProcList()
        count = 0
        state = 0

        for a_proc in pl:
            if re.match(config,a_proc.proc):
                count = count + 1
                state = 1
        
	self.ncc.newData("proc/running:state",config,state)
	self.ncc.newData("proc/running:cur",config,count)

    def getProcList(self):
        # Get the process list
        # This works on both FreeBSD and Linux, so don't gate it.

        # if 'linux2' == sys.platform or 'linux-i386' == sys.platform:
        if 'sunos5' == sys.platform:
            (status, output) = commands.getstatusoutput('/usr/ucb/ps ax')
        else:
            (status, output) = commands.getstatusoutput('/bin/ps ax')

        lines = string.split(output, "\n")

        # Remove the first line
        lines = lines[1:]

        d = []
        for l in lines:
            try:
                (pid, tty, stat, time, proc) = string.split(l, None, 4)
            except:
                print "Bad Proc Line [%s]" % (l)
                continue

            # Avoid the tail of a log problem
            if string.find(proc, 'tail') != -1:
                continue

            d.append(ProcInfo(pid,tty,stat,time,proc))
        return d


def makeMonitor(ncc):
    return ProcMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = ProcMonitor(DummyNCC())
    mon.collectData('init')

if __name__ == "__main__":
    test()
