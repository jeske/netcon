#!/neo/opt/bin/python --

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
import DiskMonitor, MemMonitor, CpuMonitor, TcpMonitor, DirQueueMonitor
import ProcMonitor
sys.path.insert(0,"MonitorPlugins/db")
import InnoTbSpcMonitor


def usage(progname):
    print "usage: %s" % progname
    print __doc__


def main(argv,stdout,environ):
    hostname = "c1" 
    nccm = nc_cmgr.NCCollectionManager(hostname)
    ncsrv = nc_srvrpc.NCServerRpc(hostname)

    config = ncsrv.getConfig()

    for module,module_config in config:
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
		print "unknown config: %s %s" % (module,module_config)
	except:
            import handle_error
            handle_error.handleException()
		
    print "=================\n" + nccm.postdata() + "\n==============\n"
    
    ncsrv.checkIn(nccm)

if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)

