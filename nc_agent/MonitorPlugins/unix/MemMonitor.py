#!/usr/bin/python

import os,sys,string
import commands
import re

class MemMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

        self.total = 0
        self.used  = 0
        self.free  = 0
        self.stotal = 0
        self.sused  = 0
        self.sfree  = 0

    def doCollectDataWin32(self):
        import win32pdh
        from win32pdhwrapper import *
        self.used = getPdhValueLong("Memory", "Pool Paged Bytes", None, 0)/1024
        self.free = getPdhValueLong("Memory", "Available KBytes", None, 0)
        self.total = self.used + self.free
        # this is not all of it, unfortunately
        self.sused = getPdhValueLong("Process", "Page File Bytes", "_Total", 0)/1024
        self.sfree = 0
        self.total = self.used + self.free

    def collectData(self,config):

        # Get the 5 min load average

        if 'linux2' == sys.platform or 'linux-i386' == sys.platform:
            f = open('/proc/meminfo', 'r')
            lines = f.readlines()
            f.close()

            # Only get the two important lines
            lines = lines[1:3]

            # Remove the new lines
            lines[0] = lines[0][:-1]
            lines[1] = lines[1][:-1]

            r  = re.compile("\S+:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)")
            m = r.search(lines[0])
            #
            # Note how we shift the number down from bytes to kilobytes
            (total, used, free, shared, buffers, cached) = map(lambda i: long(i) >> 10, m.groups())

            r  = re.compile("\S+:\s+(\d+)\s+(\d+)\s+(\d+)")
            m = r.search(lines[1])
            # Note how we shift the number down from bytes to kilobytes
            (stotal, sused, sfree, ) = map(lambda i: int(i) >> 10, m.groups())
            self.total  = total
            self.used   = used
            self.free   = free
            self.stotal = stotal
            self.sused  = sused
            self.sfree  = sfree
        elif 'freebsd' == sys.platform[:7]:

            if 'freebsd2' != sys.platform:
                # getting the free pages... the easy part
                pagesize   = string.atoi(commands.getstatusoutput('/sbin/sysctl -n hw.pagesize')[1])/1024

                totalpages = string.atoi(commands.getstatusoutput('/sbin/sysctl -n vm.stats.vm.v_page_count')[1])
                self.total = string.atoi(commands.getstatusoutput('/sbin/sysctl -n hw.physmem')[1])
                freepages  = string.atoi(commands.getstatusoutput('/sbin/sysctl -n vm.stats.vm.v_free_count')[1])
                self.free  = freepages * pagesize
                self.used  = self.total - self.free
            else:
                # Unfortunately 2.X's sysctl interface isn't as well built out.  We'll just
                # have to fudge the memory numbers but we can get somewhat detailed swap
                # information.
                self.total = self.used = string.atoi(commands.getstatusoutput('/sbin/sysctl -n hw.physmem')[1])
                self.free = 0

            (status, output) = commands.getstatusoutput('/usr/sbin/swapinfo')
            output = string.split(output, '\n')

            # remove header
            output = output[1:]

            for l in output:
                (dev, total, used, avail, percent, type) = string.split(l)
                self.stotal = total
                self.sused  = used
                self.sfree  = avail

        elif 'sunos5' == sys.platform:
            (status, output) = commands.getstatusoutput('/usr/sbin/prtconf')
            output = string.split(output, '\n')

            # second line contains: "Memory size: xxx Megabytes"
            self.total = int(string.split(output[1])[2]) * 1024

            (status, output) = commands.getstatusoutput('/usr/bin/vmstat 1 2')
            output = string.split(output, '\n')

            # last line contains data we want
            res = string.split(output[-1])
            self.free = int(res[4])

            self.used = self.total - self.free

            (status, output) = commands.getstatusoutput('/usr/sbin/swap -s')
            output = string.split(output, '=')[1]
            output = string.split(output)

            self.sused = int(output[0][:-1])
            self.sfree = int(output[2][:-1])
            self.stotal = self.sused + self.sfree

        elif 'openbsd2' == sys.platform or 'netbsd' == sys.platform[:6]:
            # OpenBSD is like freebsd2 but there's no swapinfo.

            self.total = string.atoi(commands.getstatusoutput('/sbin/sysctl -n hw.physmem')[1])

            (status, output) = commands.getstatusoutput('/usr/bin/vmstat 1 2')
            output = string.split(output, '\n')

            # last line contains data we want
            res = string.split(output[-1])
            self.free = int(res[4])

            self.used = self.total - self.free

            (status, output) = commands.getstatusoutput('/usr/sbin/pstat -s')
            output = string.split(output, '\n')

            # remove header
            output = output[1:]

            for l in output:
                (dev, total, used, avail, percent, type) = string.split(l)
                self.stotal = total
                self.sused  = used
                self.sfree  = avail
        
        elif sys.platform == 'darwin1':
            # Darwin hasn't caught up with FreeBSD in the vm stats department.
            # We can only really pull the size of the swapfiles in
            # /private/var/vm, and what we can glean from vm_stat.
            # First we need the pagesize.
            (status, output) = commands.getstatusoutput('/usr/sbin/sysctl -n hw.pagesize')
            pagesize = int(output)
            # now the vm_stat output for the page stats..
            (status, output) = commands.getstatusoutput('/usr/bin/vm_stat')
            output = string.split(output, '\n')
            sstats = []
            for line in output[1:-1]:
               sstats.append(float(string.split(line, ':')[1]))
            # should be pairs of label:#pgs now
            self.free = sstats[0] * pagesize
            # used = active + inactive + wired
            self.used = (sstats[1] + sstats[2] + sstats[3]) * pagesize
            self.total = self.used + self.free

            # Now for swap ...  
            darwinswappath = '/private/var/vm'
            sfiles = os.listdir(darwinswappath)
            self.sused = 0
            for file in sfiles:
                self.sused = self.sused + os.stat(os.path.join(darwinswappath, file))[stat.ST_SIZE]
            # Fudge :( Trigger only looks at self.sused anyway.
            self.sused = self.sused / 1024
            self.sfree = 0
            self.stotal = self.sused
        elif 'win32' == sys.platform:
            self.doCollectDataWin32()
        
        else:
            self.total  = 0
            self.used   = 0
            self.free   = 0
            self.stotal = 0
            self.sused  = 0
            self.sfree  = 1

	self.ncc.newData("machine/memory:total","",self.total)
	self.ncc.newData("machine/memory:cur","",self.used)
	self.ncc.newData("machine/memory:free","",self.free)
	self.ncc.newData("machine/memory:total","s",self.stotal)
	self.ncc.newData("machine/memory:cur","s",self.sused)
	self.ncc.newData("machine/memory:free","s",self.sfree)



def makeMonitor(ncc):
    return MemMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = MemMonitor(DummyNCC())
    mon.collectData()

if __name__ == "__main__":
    test()
