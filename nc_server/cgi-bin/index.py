#!/usr/bin/env python

import tstart

from CSPage import Context
from nc_page import NCPage

import re,time,string

import neo_cgi,neo_util
import db_netcon

import odb


class IndexPage(NCPage):
    def setup(self):
	hdf = self.ncgi.hdf
	q_incident_id = hdf.getIntValue("Query.incident_id",-1)

	if q_incident_id != -1:
	    try:
		incident = self.ndb.incidents.fetchRow(
		    ('incident_id', q_incident_id) )
		if incident.state == db_netcon.kStateNew:
		    incident.state = db_netcon.kStateViewed
		    # make note!
		    incident.save()
	    except odb.eNoMatchingRows:
		#  no such incident id
		hdf.setValue("CGI.Error.no_such_incident_id",str(q_incident_id))
		q_incident_id = -1
		hdf.setValue("Query.incident_id","")
		pass
	
    def Action_SaveInfo(self):
	hdf = self.ncgi.hdf
	q_incident_id = hdf.getIntValue("Query.incident_id",-1)
	q_name = hdf.getValue("Query.inc_name","")
	q_newstate = hdf.getValue("Query.newstate","")
	q_note = string.strip(hdf.getValue("Query.note",""))

	incident = self.ndb.incidents.fetchRow(
	    ('incident_id', q_incident_id) )
	incident.name = q_name
	if q_newstate == "ack":
	    incident.state = db_netcon.kStateAck
	elif q_newstate == "watched":
	    incident.state = db_netcon.kStateWatched
	    # compute watch until
	elif q_newstate == "resolved":
	    incident.state = db_netcon.kStateResolved
	    incident.is_active = 0
	incident.save()

	if q_note:
	    event = self.ndb.incident_event_audit.newRow()
	    event.incident_id = incident.incident_id
	    event.occured_at = int(time.time())
	    event.note = q_note
	    event.save()
	
	self.redirectUri("index.py?incident_id=%s" % hdf.getValue("Query.incident_id", ""))

	
    def Action_MoveTo(self):
	hdf = self.ncgi.hdf
	q_move_dest = hdf.getIntValue("Query.move_dest",-1)

	dest = None
	
	if q_move_dest != -1:
	    try:
		dest = self.ndb.incidents.fetchRow(
		    ('incident_id', q_move_dest) )
	    except odb.eNoMatchingRows:
		pass
		
	if dest is None:
	    dest = self.ndb.incidents.newRow()
	    dest.start = int(time.time())
	    dest.end   = int(time.time())
	    dest.is_active = 1
	    # create as already acknowldged
	    dest.state = db_netcon.kStateAck 
	    dest.save()

	# iterate through errors to move...
	ehdf = hdf.getObj("Query.mverr")
	if ehdf and ehdf.child():
	    ehdf = ehdf.child()
	    while ehdf:
		try:
		    err = self.ndb.incident_errors.fetchRow(
			('incident_error_map_id', int(ehdf.name())) )
		    err.incident_id = dest.incident_id
		    err.save()
		except odb.eNoMatchingRows:
		    pass

		ehdf = ehdf.next()
	
	self.redirectUri("index.py?incident_id=%s" % hdf.getValue("Query.incident_id", ""))
	
    def exportIncident(self,incident,prefix):
	incident.hdfExport(prefix,self.ncgi.hdf)

	events = self.ndb.incident_event_audit.fetchRows(
	    ('incident_id', incident.incident_id),
	    order_by =['occured_at desc'])

	events.hdfExport(prefix + ".events",self.ncgi.hdf)

	errs = self.ndb.incident_errors.fetchRows( ('incident_id', incident.incident_id) )

	ne = 0
	for an_err in errs:
	    eprefix = prefix + ".errors.%d" % ne
	    ne = ne + 1
	    an_err.hdfExport(eprefix, self.ncgi.hdf)

	    # unpack error info
	    ehdf = an_err.unpackErrorInfo()
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

	    # export current trigger data for this trigger!
	    tsrc = self.ndb.services.getService("trigger/%s:state" % trigger_id)
	    try:
		tdata = self.ndb.monitor_state.fetchRow(
		    [ ('source_id', source_id),
		      ('serv_id', tsrc.serv_id) ])
		tdata.hdfExport(eprefix + ".tdata", self.ncgi.hdf)
	    except odb.eNoMatchingRows:
		pass

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
    
    def display(self):
	# current time
	self.ncgi.hdf.setValue("CGI.CurrentTime",str(int(time.time())))
	
	# cur incident
	q_incident_id = self.ncgi.hdf.getIntValue("Query.incident_id",-1)
	
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
	    if not re.match("trigger/[0-9]",a_service.namepath):
		a_service.hdfExport("CGI.show_services.%d" % a_service.serv_id,
				    self.ncgi.hdf)
		
		
	
        # load current incidents
        active = self.ndb.incidents.getAllActiveIncidents()

        n = 0
        for incident in active:
            prefix = "CGI.active_incidents.%s" % n
	    n = n + 1
	    incident.hdfExport(prefix,self.ncgi.hdf)

	    # find out if incident is current good or bad...
	    errs = self.ndb.incident_errors.fetchRows( ('incident_id',
							incident.incident_id) )

	    good_count = 0
	    bad_count = 0
	    for an_err in errs:
		# unpack error info
		ehdf = an_err.unpackErrorInfo()
		trigger_serv_id = ehdf.getIntValue("trigger_serv_id",-1)
		source_id = ehdf.getIntValue("source",-1)

		# export trigger details
		trigger_id = ehdf.getIntValue("trigger_id",-1)

		# export current trigger data for this trigger!
		tsrc = self.ndb.services.getService("trigger/%s:state" % trigger_id)
		try:
		    tdata = self.ndb.monitor_state.fetchRow(
			[ ('source_id', source_id),
			  ('serv_id', tsrc.serv_id) ])
		    if tdata.value == 1:
			bad_count = bad_count + 1
		    elif tdata.value == 0:
			good_count = good_count + 1
		    else:
			log("!!!!! trigger is not 1/0")

		except odb.eNoMatchingRows:
		    pass

	    self.ncgi.hdf.setValue(prefix + ".bad_count", str(bad_count))
	    self.ncgi.hdf.setValue(prefix + ".good_count", str(good_count))


	if q_incident_id != -1:
	    cur_incident = self.ndb.incidents.fetchRow(
		('incident_id', q_incident_id) )
	    
	    self.exportIncident(cur_incident,"CGI.incident")

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



