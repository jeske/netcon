#!/usr/bin/python

import os,sys,string, time

class DirQueueMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

    def collectData(self,config):
	c = shallowFileCount(config)
	
	self.ncc.newData("dir/filecount:cur",config,c)

def shallowFileCount(d):
    c = 0

    z = os.listdir(d)
    for f in z:
        p = os.path.join(d, f)
        if os.path.isdir(p):
            c = c + len(os.listdir(p))
        else:
            c = c + 1

    return c

def makeMonitor(ncc):
    return DirQueueMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = DirQueueMonitor(DummyNCC())
    mon.collectData('/etc')

if __name__ == "__main__":
    test()
