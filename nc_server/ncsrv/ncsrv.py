#!/neo/opt/bin/python

import tstart

from log import *
import time, string
import db_netcon

import wordwrap

import whrandom
import nc_datamgr, nc_triggermgr, nc_incidentmgr, nc_trends

import neo_cgi, neo_util

import odb


class NCSrv:
    def __init__(self):
        # connect
        self.ndb = db_netcon.netcon_connect()

    def run_trends(self):
	ndb = self.ndb

	print "---------- TREND STAGE -----------------"
	try:
	    trendsmanager = nc_trends.NCTrendsManager(ndb)
	    trendsmanager.computeAllTrends()
	except:
	    import handle_error
	    handle_error.handleException()
	

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
	name = "(unknown)"
	try:
	    trigger = inc_error_obj.getTriggerRow()
	    source  = inc_error_obj.getSourceRow()
	    state   = inc_error_obj.getSourceStateRow()
	    serv    = self.ndb.services.fetchRow(
		('serv_id', state.serv_id) )
	    mach    = self.ndb.machines.fetchRow(
		('mach_id', source.source_mach_id) )

	    name = "%s(%s:%s) %s:%s=%s" % \
		    (trigger.name,mach.name,source.source_name,
		     serv.namepath,serv.type,state.value)
	    log("name = %s" % name)
	    
	except odb.eNoMatchingRows:
	    pass

	return name
        
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

        log("%d active incidents to check" % len(act_inc))

	if not act_inc:
	    return

	notification = ""
	summary = None

	# compose information about errors...
	active_count = 0
	
	for inc in act_inc:
	    ierrs = inc.getErrors()

	    # find out the current states of the errors
	    count = 0
	    bad_count = 0
	    for err in ierrs:
		try:
		    state = err.getStateRow()
		    count = count + 1
		    if state.value != 0:
			bad_count = bad_count + 1
		except odb.eNoMatchingRows:
		    pass

	    log("incident %s:%s,  count=%s,bad_count=%s" %
		(inc.incident_id,inc.name,count,bad_count))
		
	    if bad_count == 0:
		log("   skipping incident notify...")
		continue

	    active_count = active_count + 1
	    errs = []
	    for err in ierrs:
		# figure out the real name of the error!
		errs.append(self.nameForError(err))
		
	    inc_info = "NC[%d] %d errors: %s" % (inc.incident_id, len(ierrs),string.join(errs,", "))
	    
	    if summary is None:
		summary = inc_info[:50]
	    notification = notification + inc_info + "\n"
	# compose real msg

	if active_count > 1:
	    notification = "[%s incidents] \n" % len(act_inc)
	    summary = "[%s incidents]" % len(act_inc)

	if active_count == 0:
	    # no notifications!
	    return
	
	import sendmail
	
	RECIP = ["blong-page@fiction.net", "jeske-pagenc@neotonic.com"]

        # for debugging only:
	RECIP = ["jeske@neotonic.com"]
	# RECIP = ["jeske-pagenc@neotonic.com"]
	
	for recip in RECIP:
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
	self.run_trends()
	
	self.run_triggers()  # run triggers and generate errors..

	self.run_incident_management() # coalesc errors into incidents

	self.run_notification() # check current incidents and generate notifications

def main():
    ncsrv = NCSrv()
    ncsrv.run()

if __name__ == "__main__":
    main()
