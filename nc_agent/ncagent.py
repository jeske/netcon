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
    
    mon = DiskMonitor.makeMonitor(nccm)
    mon.collectData()

    mon = MemMonitor.makeMonitor(nccm)
    mon.collectData()

    mon = CpuMonitor.makeMonitor(nccm)
    mon.collectData()

    print nccm.postdata()

    ncsrv = nc_srvrpc.NCServerRpc(hostname)
    ncsrv.checkIn(nccm)

if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)

