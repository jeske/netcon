#!/usr/bin/python

import os,sys,string
import commands
import re

class CpuMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

	self.currentLoad = 0
	self.uptime = 0

    def doCollectDataWin32(self):
        import win32pdh
        import win32pdhquery

        try:
            han = win32pdh.OpenQuery()
            thepath = win32pdh.MakeCounterPath((None, "Processor", "_Total", None, 0, "% Processor Time"))
            counter_handle = win32pdh.AddCounter(han, thepath)
            win32pdh.CollectQueryData(han) # do the deed
            win32pdh.CollectQueryData(han) # needs to be done a few times to flush bogus values
            self.currentLoad = float(win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)[1])
            win32pdh.CloseQuery(han)
        except:
            print "Error collecting CPU usage data"
            self.currentLoad = 0
            raise

        # next up:  System\System Up Time  
        try:
            han = win32pdh.OpenQuery()
            thepath = win32pdh.MakeCounterPath((None, "System", None, None, 0, "System Up Time"))
            counter_handle = win32pdh.AddCounter(han, thepath)
            win32pdh.CollectQueryData(han) # do the deed
            self.uptime = float(win32pdh.GetFormattedCounterValue(counter_handle, win32pdh.PDH_FMT_LONG)[1])
            win32pdh.CloseQuery(han)
        except:
            print "Error collecting CPU usage data"
            self.uptime = 0
            raise

        # self.uptime = self.uptime * 60
        
    def collectData(self):

        # Get the 5 min load average
        if 'linux2' == sys.platform or 'linux-i386' == sys.platform:
            f = open('/proc/loadavg', 'r')
            data = f.read()
            data = data[:-1]          # Remove the newline
            f.close()
            (load1min, load5min, load15min, nr_runningNr_tasks, last_pid) = string.split( data, " ")

            f = open('/proc/uptime', 'r')
            data = f.read()
            data = data[:-1]          # Remove the newline
            f.close()
            (uptime, idletime) = string.split( data, " ")
            self.uptime      = float(uptime)
            self.currentLoad = float(load5min)

        elif 'freebsd' == sys.platform[:7]:
            data = commands.getstatusoutput('/sbin/sysctl vm.loadavg')
            # want the 4th argument of : (0, 'vm.loadavg: { 0.17 0.10 0.02 }')
            (title, bracket, load1min, load5min, load10min) = string.split(data[1], " ", 4)
            self.currentLoad = float(load5min)
            # kern.boottime: { sec = 941599162, usec = 949487 } Tue Nov  2 19:19:22 1999
            data = commands.getstatusoutput('/sbin/sysctl kern.boottime')
            (title, bracket, blah, blah2, starttime, rest) = string.split(data[1], " ", 5)
            starttime = string.translate(starttime, string.maketrans(',', ' '))
            self.uptime = float(time.time() - string.atof(starttime))

        elif 'sunos5' == sys.platform:
            # Solaris - we can get the uptime, but we must punt on the uptime
            data = commands.getstatusoutput('/usr/bin/uptime')
            if data[0] == 0:
                (junk, loads) = string.split(data[1], ": ")
                (load1min, load5min, load10min) = string.split(loads, ", ")
                self.currentLoad = string.atof(load5min)

                # Now get the mtime of /proc/0
                startTime = os.stat('/proc/0')[8]
                self.uptime = time.time() - startTime

        elif 'darwin' == sys.platform[:6] or 'openbsd' == sys.platform[:7] or 'netbsd' == sys.platform[:6]:
            data = commands.getstatusoutput('/sbin/sysctl -n vm.loadavg')
            # want the 3th argument of : (0, '0.17 0.10 0.02')
            (load1min, load5min, load10min) = string.split(data[1], " ", 2)
            self.currentLoad = float(load5min)
            # -n on this sysctl returns the unix timestamp -- handy.
            (status, output) = commands.getstatusoutput('/sbin/sysctl -n kern.boottime')
            self.uptime = float(time.time() - int(output))

        elif 'win32' == sys.platform:
            self.doCollectDataWin32()
	else:
	    raise "unknown machine type"

	self.ncc.newData("machine/cpu/uptime:seconds","",self.uptime)
	self.ncc.newData("machine/cpu/load:cur","",self.currentLoad)
	

def makeMonitor(ncc):
    return CpuMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = CpuMonitor(DummyNCC())
    mon.collectData()

if __name__ == "__main__":
    test()

