import odb

from log import *
import neo_cgi
import neo_util

class NCIncidentManager:
    def __init__(self,ndb):
        self.ndb = ndb

    def updateIncidents(self):
        # make sure all current errors are represented in incidents
        self.scanErrors()

    def scanErrors(self):
        ndb = self.ndb
        # fetch out all trigger/* services
        services = ndb.services.getMatchingServices("trigger/")

        log("scan errors (%s)" % len(services))

        # fetch out recent data for these services to find current errors
        for a_service in services:
            log("check service: %s" % repr(a_service))

            statedata = ndb.monitor_state.fetchRows( ('serv_id', a_service.serv_id) )

            for edata in statedata:
		ehdf = neo_util.HDF()
		ehdf.setValue("trigger_serv_id", str(a_service.serv_id))
		ehdf.setValue("source", str(edata.source_id))

		incident_error_key = ehdf.dump()

		if edata.value == 0:
		    # no error to report
		    break

		log("report error for: %s" % repr(incident_error_key))

                try:
                    ierror = ndb.incident_errors.findActiveError(incident_error_key)
		    log("found active error! %s" % repr(ierror))

		    incident = ndb.incidents.fetchRow(
			('incident_id', ierror.incident_id) )
		    
		    if edata.pend > incident.end:
			incident.is_active=1
			incident.end = edata.pend
			incident.save()
                    
                except odb.eNoMatchingRows:
		    # update the incident
		    curincident = ndb.incidents.getActiveIncident(create=1,
								  event_time=edata.pend)
		    # create the error
		    ierror = ndb.incident_errors.newRow()
		    ierror.incident_id = curincident.incident_id
		    ierror.error_spec=incident_error_key
		    ierror.save()

		    log("new error: %s" % repr(ierror))
		    




