#!/usr/bin/python --

#
# nc_agent.py - This is the monitoring agent for our system
#
"""
  nc_agent.py - Netcon Monitoring Agent

"""

import os, sys, string, getopt
import time

import nc_cmgr, nc_srvrpc

# hardcoded path hackery...
sys.path.insert(0,"/home/jeske/netcon/nc_agent/MonitorPlugins/unix")
sys.path.insert(0,"/neo/nc_agent/MonitorPlugins/unix")

sys.path.insert(0,"MonitorPlugins/unix")
import DiskMonitor, MemMonitor, CpuMonitor


def usage(progname):
    print "usage: %s" % progname
    print __doc__


def main(argv,stdout,environ):
    hostname = "c1" 
    nccm = nc_cmgr.NCCollectionManager(hostname)
    ncsrv = nc_srvrpc.NCServerRpc(hostname)

    config = ncsrv.getConfig()

    for module,module_config in config:
	if module == "disk":
	    mon = DiskMonitor.makeMonitor(nccm)
	    mon.collectData(module_config)
	elif module == "mem":
	    mon = MemMonitor.makeMonitor(nccm)
	    mon.collectData(module_config)
	elif module == "cpu":
	    mon = CpuMonitor.makeMonitor(nccm)
	    mon.collectData(module_config)
	elif module == "tcp":
	    mon = TcpMonitor.makeMonitor(nccm)
	    mon.collectData(module_config)
	else:
	    print "unknown config: %s %s" % (module,module_config)
		
    print "=================\n" + nccm.postdata() + "\n==============\n"
    
    ncsrv.checkIn(nccm)

if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)

