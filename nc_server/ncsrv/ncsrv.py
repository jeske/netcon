#!/neo/opt/bin/python

import tstart

from log import *
import time, string
import db_netcon

import whrandom
import nc_datamgr, nc_triggermgr, nc_incidentmgr

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
        
    def run_notification(self):
        ndb = self.ndb

	# this needs to be changed to retain state per user
        
	# for all active incidents...
	act_inc = ndb.incidents.getAllActiveIncidents()

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
		errs.append(str(err.incident_error_map_id))
		
	    inc_info = "%d errors: %s" % (len(ierrs),string.join(errs,","))
	    if summary is None:
		summary = inc_info[:50]
	    notification = notification + inc_info + "\n"
	# compose real msg

	import sendmail
	for recip in ["jeske@neotonic.com"]:
	    bodyp = []
	    bodyp.append("To: %s" % recip)
	    bodyp.append("From: netcon@neotonic.com")
	    bodyp.append("Subject: %s" % summary)
	    bodyp.append("")
	    bodyp.append(notification)

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
