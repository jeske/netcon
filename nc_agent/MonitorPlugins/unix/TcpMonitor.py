#!/usr/bin/python

import os,sys,string, time
import commands
import re
import tcp

class TcpMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

    def collectData(self,config):
	host,port = string.split(config,":")

	start = time.time()
	t = tcp.TCP(host,80)
	connect_time = time.time() - start
	t.set_debuglevel(1)
	t.send("GET / HTTP/1.1\nHost: %s\n\n" % host)
	print 'Valid: %s' % (t.valid)
	errcode, errmsg = t.getreply(45)

	self.ncc.newData("tcp/connect:state","80",1,hostname=host)
	self.ncc.newData("tcp/connect:time","80",connect_time,hostname=host)


def makeMonitor(ncc):
    return TcpMonitor(ncc)

def test():
    class DummyNCC:
        def newData(self,*a):
            print string.join(map(lambda x:str(x),a)," ")
    mon = TcpMonitor(DummyNCC())
    mon.collectData('localhost:25')

if __name__ == "__main__":
    test()
