#!/neo/opt/bin/python

import tstart

from log import *
import time, string
import db_netcon

import wordwrap

import whrandom
import nc_datamgr, nc_triggermgr, nc_incidentmgr

import neo_cgi, neo_util

import odb


class NCSrv:
    def __init__(self):
        # connect
        self.ndb = db_netcon.netcon_connect()

    def run_triggers(self):
        ndb = self.ndb

        print "---------- TRIGGER STAGE -----------------"

        triggermanager = nc_triggermgr.NCTriggerManager(ndb)
        triggermanager.runAllTriggers()
        
    def run_incident_management(self):
        ndb = self.ndb

        print "---------- INCIDENT STAGE -----------------"

        incidentmanager = nc_incidentmgr.NCIncidentManager(ndb)
        incidentmanager.updateIncidents()

    def nameForError(self,inc_error_obj):
        # look up the trigger name
	ehdf = neo_util.HDF()
	ehdf.readString(inc_error_obj.error_spec)
	trigger_id = ehdf.getIntValue("trigger_id",-1)

	try:
	    trigger = self.ndb.role_triggers.fetchRow( ('trigger_id', trigger_id) )
	except odb.eNoMatchingRows:
	    return "(unknown)"

	return trigger.name
        
##     Subject: NC[64] 2 critical, 10 error, 3 warning
##     (8/15 12:05am)
##     2 critical: Web(www.trakken.com), Web(www.neotonic.com)...
##     10 error: Disk(c1), Disk(c4)...
##     3 warning: Mem(c1), Mem(c4), Bugs(c9)

##     Subject: NC[64] View/Acknowledge (blong)
##     (8/15 12:30am)

##     Subject: NC[64] RequiresUpdate (blong)
##     (8/15 12:40am)
##     Please update the online status or Netcon will escelate!

##     Subject: NC[64] Note (blong)
##     (8/15 12:42am)
##     Navisite is aware of the problem, and will call me back...

##     Subject: NC[64] Escelate! (30min) 2 critical, 10 error, 3 warning
##     (8/15 12:45am)
##     2 critical: Web(www.trakken.com), Web(www.neotonic.com)...
##     10 error: Disk(c1), Disk(c4)...
##     3 warning: Mem(c1), Mem(c4), Bugs(c9)

        
    def run_notification(self):
        ndb = self.ndb
        log("----- notifications ---- ")

	# this needs to be changed to retain state per user
        
	# for all active incidents...
	act_inc = ndb.incidents.getIncidentsForNotification()

        log("%d incidents to notify about" % len(act_inc))

	if not act_inc:
	    return

	notification = ""
	summary = None

	if len(act_inc) > 1:
	    notification = "[%s incidents] \n" % len(act_inc)
	    summary = "[%s incidents]" % len(act_inc)

	# compose information about errors...

	for inc in act_inc:
	    ierrs = self.ndb.incident_errors.fetchRows(
		('incident_id', inc.incident_id) )
	    errs = []
	    for err in ierrs:
		# figure out the real name of the error!
		errs.append(self.nameForError(err))
		
	    inc_info = "NC[%d] %d errors: %s" % (inc.incident_id, len(ierrs),string.join(errs,", "))
	    
	    if summary is None:
		summary = inc_info[:50]
	    notification = notification + inc_info + "\n"
	# compose real msg

	import sendmail
	for recip in ["jeske@neotonic.com", "jeske-pagenc@neotonic.com"]:
	    bodyp = []
	    bodyp.append("To: %s" % recip)
	    bodyp.append("From: netcon@neotonic.com")
	    bodyp.append("Subject: %s" % summary)
	    bodyp.append("")
	    bodyp.append(wordwrap.WordWrap(notification))

	    body = string.join(bodyp,"\n")

	    # send notification

	    BOUNCE_TO = "jeske@neotonic.com"
	    sendmail.sendmail(BOUNCE_TO,[recip],body)


    # main run!!!

    def run(self):
	self.run_triggers()  # run triggers and generate errors..

	self.run_incident_management() # coalesc errors into incidents

	self.run_notification() # check current incidents and generate notifications

def main():
    ncsrv = NCSrv()
    ncsrv.run()

if __name__ == "__main__":
    main()
