#!/usr/bin/env python

import tstart

from CSPage import Context
from nc_page import NCPage

import re

import neo_cgi,neo_util

import odb


class ViewDataHistoryPage(NCPage):
    def display(self):
	hdf = self.ncgi.hdf
	sets = []

	nset = 0
	while 1:
	  q_service_id = hdf.getIntValue("Query.serv_id.%s" % nset,-1)
	  if q_service_id == -1: break
	  q_source_id  = hdf.getIntValue("Query.source_id.%s" % nset,-1)

	  sets.append((nset, q_service_id, q_source_id))
	  nset = nset + 1


	if len(sets) == 0:
	  q_service_id = hdf.getIntValue("Query.serv_id",-1)
	  q_source_id  = hdf.getIntValue("Query.source_id",-1)

	  sets.append((0, q_service_id, q_source_id))

	for (nset, q_service_id, q_source_id) in sets:
	  prefix = "CGI.dataset.%s" % nset
	  service = self.ndb.services.fetchRow( ('serv_id', q_service_id) )
	  service.hdfExport(prefix + ".service", self.ncgi.hdf)

	  source = self.ndb.monitor_sources.fetchRow(
	      ('source_id', q_source_id) )
	  source.hdfExport(prefix + ".source", self.ncgi.hdf)

	  smach = self.ndb.machines.fetchRow(
	      ('mach_id', source.source_mach_id) )
	  smach.hdfExport(prefix + ".source.machine",self.ncgi.hdf)

	  h_data = self.ndb.monitor_history.fetchRows(
	      [ ('serv_id', q_service_id),
		('source_id', q_source_id)] )

	  h_data.hdfExport(prefix + ".history", self.ncgi.hdf)
	
	

if __name__ == "__main__":
    context = Context()
    ViewDataHistoryPage(context, pagename="viewDataHistory").start()



