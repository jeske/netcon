#!/usr/bin/python

import os,sys,string
import commands
import re

class DiskMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

        self.diskList  = []

        self.reg1 = re.compile("(\d+).")
        self.reg2 = re.compile(".+/(.+)")

    def collectData(self,config):
        # Get disk usage
        if 'linux2' == sys.platform or 'linux-i386' == sys.platform:
            DF_CMD = "/bin/df -k -x tmpfs -x swap"
            # DF_CMD = "/bin/df -k -l"
            (status, output) = commands.getstatusoutput(DF_CMD)
        elif 'freebsd' == sys.platform[:7] or 'openbsd' == sys.platform[:7] or 'netbsd' == sys.platform[:6]:
            (status, output) = commands.getstatusoutput('/bin/df -kt ufs')
        elif 'sunos5' == sys.platform:
            (status, output) = commands.getstatusoutput('/usr/ucb/df -kF ufs')
        elif 'darwin' == sys.platform[:6]:
            (status, output) = commands.getstatusoutput('/bin/df -kt hfs,ufs')
        else:
            raise "unknown platform: %s" % sys.platform

        lines = string.split(output, "\n")
        # Remove the first line
        lines = lines[1:]

        for l in lines:
            #(device, total, totalUsed, available, percent, mountPoint)
            x = string.split(l)

            m = self.reg2.search(x[0])
            x[0] = m.group(1)


            # unpack
            device,total,totalUsed,available,percent,mountPoint = x

            print 'size info', x
            self.diskList.append(x)

            self.ncc.newData("disk/size:total",device,available)
            self.ncc.newData("disk/size:cur",device,totalUsed)
            self.ncc.newData("disk/size:pct",device,percent)

        # Get disk inode usage
        if 'linux2' == sys.platform or 'linux-i386' == sys.platform:
            (status, output) = commands.getstatusoutput('/bin/df -it ext2 -t ext3')
        elif 'freebsd' == sys.platform[:7]:
            (status, output) = commands.getstatusoutput('/bin/df -it ufs')
        elif 'sunos5' == sys.platform:
            (status, output) = commands.getstatusoutput('/usr/ucb/df -i')

        lines = string.split(output, "\n")
        # Remove the first line
        lines = lines[1:]

        for l in lines:
            x = string.split(l)

            m = self.reg2.search(x[0])
            x[0] = m.group(1)

            if sys.platform[:7] == 'freebsd':
                #(device, total, totalUsed, available, percent, iused, ifree, ipercent, mountPoint)
                x = x[0:1] + x[5:8]
            elif sys.platform == 'sunos5':
                #(device, totalUsed, available, percent, mountPoint)
                x = x
            else:
                #(device, total, totalUsed, available, percent, mountPoint)
                x = x[0:1] + x[2:]

            print 'inode info:', x
            
            # unpack!
            device,totalUsed, available, percent,mountPoint = x
            # report data
            self.ncc.newData("disk/inodes:total",device,available)
            self.ncc.newData("disk/inodes:cur",device,totalUsed)
            self.ncc.newData("disk/inodes:pct",device,percent)
                
            # Locate the disk and append the list
            for disk in self.diskList:
                if disk[0] == x[0]:
                    for d in x[1:]:
                        disk.append(d)

def makeMonitor(ncc):
    return DiskMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = DiskMonitor(DummyNCC())
    print repr(mon.collectData())

if __name__ == "__main__":
    test()
