#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import re

import neo_cgi,neo_util

import odb


class ViewServicePage(NCPage):
    def display(self):
	hdf = self.ncgi.hdf
	q_service_id = hdf.getIntValue("Query.serv_id",-1)

	service = self.ndb.services.fetchRow( ('serv_id', q_service_id) )
	service.hdfExport("CGI.service", self.ncgi.hdf)

	cdata = self.ndb.monitor_state.fetchRows(
	    ('serv_id', q_service_id) )

	source_hash = {}
	for cd in cdata:
	    source_hash[cd.source_id] = 1

	for source_id in source_hash.keys():
	    source = self.ndb.monitor_sources.fetchRow(
		('source_id', source_id) )
	    source.hdfExport("CGI.sources.%d" % source_id, self.ncgi.hdf)

	    smach = self.ndb.machines.fetchRow( ('mach_id', source.source_mach_id) )
	    smach.hdfExport("CGI.sources.%d.machine" % source_id, self.ncgi.hdf)

	# don't forget to export the data
	cdata.hdfExport("CGI.cdata", self.ncgi.hdf)
	n = 0
	for acd in cdata:
	    prefix = "CGI.cdata.%d" % n
	    n = n + 1
	    acd.hdfExport(prefix,self.ncgi.hdf)
	    
	    if service.type == "seconds":
		vf = "%f days" % (acd.value/86400.0)
	    else:
		vf = "%f" % acd.value

	    self.ncgi.hdf.setValue(prefix + ".value",vf)

	
	

if __name__ == "__main__":
    context = Context()
    ViewServicePage(context, pagename="viewService").start()



