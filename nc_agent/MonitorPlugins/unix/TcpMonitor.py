#!/usr/bin/python

import os,sys,string, time
import commands
import re
import tcp

class TcpMonitor:
    def __init__(self,ncc):
        self.ncc = ncc

    def collectData(self,config):
	host,sport = string.split(config,":")
        port = string.atoi(sport)

	start = time.time()

	success = 0
	try:
	    t = tcp.TCP(host,port)
	    connect_time = time.time() - start
	    t.set_debuglevel(1)

	    if port == 80:
		t.send("GET / HTTP/1.1\nHost: %s\n\n" % host)

            errcode, errmsg = t.getreply(45)
            
            print 't.Valid: %s, errcode: %s' % (t.valid,errcode)

	    if t.valid:
		success = 1
	except os.error, reason:
	    pass
        except:
            print "unknown error.."

	self.ncc.newData("tcp/connect:state",str(port),success,hostname=host)
	self.ncc.newData("tcp/connect:time",str(port),connect_time,hostname=host)


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
