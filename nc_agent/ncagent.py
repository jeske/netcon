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

sys.path.insert(0,"MonitorPlugins/unix")
import DiskMonitor


def usage(progname):
    print "usage: %s" % progname
    print __doc__


def main(argv,stdout,environ):
    nccm = nc_cmgr.NCCollectionManager()
    
    mon = DiskMonitor.makeMonitor(nccm)
    mon.collectData()

    nccm.report()

    ncsrv = nc_srvrpc.NCServerRpc("http://c1.neotonic.com/netcon/agentCheckIn.py")
    ncsrv.checkIn()

if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)

