#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import re

import neo_cgi,neo_util

import odb


class ViewDataHistoryPage(NCPage):
    def display(self):
	hdf = self.ncgi.hdf
	q_service_id = hdf.getIntValue("Query.serv_id",-1)
	q_source_id  = hdf.getIntValue("Query.source_id",-1)

	service = self.ndb.services.fetchRow( ('serv_id', q_service_id) )
	service.hdfExport("CGI.service", self.ncgi.hdf)

	source = self.ndb.monitor_sources.fetchRow(
	    ('source_id', q_source_id) )
	source.hdfExport("CGI.source", self.ncgi.hdf)

	smach = self.ndb.machines.fetchRow(
	    ('mach_id', source.source_mach_id) )
	smach.hdfExport("CGI.source.machine",self.ncgi.hdf)

        h_data = self.ndb.monitor_history.fetchRows(
	    [ ('serv_id', q_service_id),
	      ('source_id', q_source_id)],
	    limit_to=200, order_by=["pend desc"])

	h_data.hdfExport("CGI.history", self.ncgi.hdf)
	
	

if __name__ == "__main__":
    context = Context()
    ViewDataHistoryPage(context, pagename="viewDataHistory").start()



