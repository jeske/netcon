#!/usr/bin/env python

#
# nc_agent.py - This is the monitoring agent for our system
#
"""
  nc_agent.py - Netcon Monitoring Agent

"""

import os, sys, string, getopt
import time
import socket

import nc_cmgr, nc_srvrpc

# hardcoded path hackery...
sys.path.insert(0,"/home/jeske/netcon/nc_agent/MonitorPlugins/unix")
sys.path.insert(0,"/neo/nc_agent/MonitorPlugins/unix")

sys.path.insert(0,"MonitorPlugins/unix")
import DiskMonitor, MemMonitor, CpuMonitor, TcpMonitor, DirQueueMonitor
import ProcMonitor
sys.path.insert(0,"MonitorPlugins/db")
import InnoTbSpcMonitor

def myhost():
    host = socket.gethostname()
    hp = string.split(host,".")
    if len(hp) > 2:
        hp = hp[:-2]
    return string.join(hp,".")

def usage(progname):
    print "usage: %s" % progname
    print __doc__

import ihooks
def fallback_monitor(mon_name, nccm, module_config):
    ml = ihooks.ModuleImporter()
    mod = ml.import_module("%sMonitor" % mon_name)
    mon = mod.makeMonitor(nccm)
    mon.collectData(module_config)

def main(argv,stdout,environ):
    hostname = myhost()
    nccm = nc_cmgr.NCCollectionManager(hostname)
    ncsrv = nc_srvrpc.NCServerRpc(hostname)

    config = ncsrv.getConfig()

    for module,module_config in config:
        print "config: %s/%s" % (module,module_config)
	try:
	    if module == "Disk":
		mon = DiskMonitor.makeMonitor(nccm)
		mon.collectData(module_config)
	    elif module == "Mem":
		mon = MemMonitor.makeMonitor(nccm)
		mon.collectData(module_config)
	    elif module == "Cpu":
		mon = CpuMonitor.makeMonitor(nccm)
		mon.collectData(module_config)
	    elif module == "Tcp":
		mon = TcpMonitor.makeMonitor(nccm)
		mon.collectData(module_config)
	    elif module == "DirQueue":
		mon = DirQueueMonitor.makeMonitor(nccm)
		mon.collectData(module_config)
            elif module == "Proc":
                mon = ProcMonitor.makeMonitor(nccm)
                mon.collectData(module_config)
            elif module == "InnoTbSpc":
                mon = InnoTbSpcMonitor.makeMonitor(nccm)
                mon.collectData(module_config)
            else:
                fallback_monitor(module, nccm, module_config)
	except:
            import handle_error
            handle_error.handleException()
		
    print "=================\n" + nccm.postdata() + "\n==============\n"
    
    ncsrv.checkIn(nccm)

if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)

