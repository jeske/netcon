#!/usr/bin/python

import os,sys,string
import commands
import re
import tcp

class TcpMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

    def collectData(self,config):
	host,port = string.split(config,":")
        tcp.TCP( host,port )

def makeMonitor(ncc):
    return TcpMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = TcpMonitor(DummyNCC())
    mon.collectData('localhost')

if __name__ == "__main__":
    test()
