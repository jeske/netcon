#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import re

import neo_cgi,neo_util

import odb


class IndexPage(NCPage):
    def display(self):
	# check for clear request
	q_clear_incident = self.ncgi.hdf.getIntValue("Query.clear_incident",-1)
	try:
	    incident = self.ndb.incidents.fetchRow(
		('incident_id', q_clear_incident) )
	    incident.is_active = 0
	    incident.save()
	except odb.eNoMatchingRows:
	    pass



	# export services
	services = self.ndb.services.fetchRows(order_by=['namepath'])
	for a_service in services:
	    a_service.hdfExport("CGI.services.%d" % a_service.serv_id,
				self.ncgi.hdf)
	
        # load current incidents
        active = self.ndb.incidents.getAllActiveIncidents()

        n = 0
        for incident in active:
            prefix = "CGI.active_incidents.%s" % n
            incident.hdfExport(prefix,self.ncgi.hdf)

            errs = self.ndb.incident_errors.fetchRows( ('incident_id', incident.incident_id) )
	    
	    ne = 0
	    for an_err in errs:
		eprefix = prefix + ".errors.%d" % ne
		ne = ne + 1
		an_err.hdfExport(eprefix, self.ncgi.hdf)
		
		# unpack error info
		ehdf = neo_util.HDF()
		ehdf.readString(an_err.error_spec)
		trigger_serv_id = ehdf.getIntValue("trigger_serv_id",-1)
		source_id = ehdf.getIntValue("source",-1)

		# export trigger details
		trigger_id = ehdf.getIntValue("trigger_id",-1)
		try:
		    trig = self.ndb.role_triggers.fetchRow(
			('trigger_id', trigger_id) )
		    trig.hdfExport(eprefix + ".trigger",self.ncgi.hdf)
		except odb.eNoMatchingRows:
		    # the trigger must have been deleted!
		    continue

		# export source information
		tsrc = self.ndb.monitor_sources.fetchRow(
		    ('source_id', source_id) )
		tsrc.hdfExport(eprefix + ".source", self.ncgi.hdf)


		# export current data for this source!
		try:
		    cdata = self.ndb.monitor_state.fetchRow(
			[ ('source_id', source_id ),
			  ('serv_id', trig.serv_id ) ] )
		    
		    cdata.hdfExport(eprefix + ".cdata", self.ncgi.hdf)
		except odb.eNoMatchingRows:
		    pass

		

        # load machines
        machines = self.ndb.machines.fetchRows(order_by=['name'])
	for a_mach in machines:
	    a_mach.hdfExport("CGI.machines.%d" % a_mach.mach_id,self.ncgi.hdf)

        # load agents
        agents = self.ndb.agents.fetchRows()
        agents.hdfExport("CGI.agents",self.ncgi.hdf)
 
        

if __name__ == "__main__":
    context = Context()
    IndexPage(context, pagename="index").start()



