import odb

from log import *

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
                incident_error_key = "service=%s(%s:%s),source=%s" % (a_service.serv_id,
                                                                      a_service.namepath,
                                                                      a_service.type,
                                                                      edata.source_id)

                try:
                    ierror = ndb.incident_errors.findActiveError(incident_error_key)
                    if edata.value == 1:
                        incident = ndb.incidents.fetchRow( ('incident_id', ierror.incident_id) )
                        if edata.pend > incident.end:
                            incident.end = edata.pend
                            incident.save()
                        
                    
                except odb.eNoMatchingRows:
                    if edata.value == 1:
                        # update the incident
                        curincident = ndb.incidents.getActiveIncident(create=1,
                                                                      event_time=edata.pend)
                        
                        # create the error
                        ierror = ndb.incident_errors.newRow()
                        ierror.incident_id = curincident.incident_id
                        ierror.error_spec=incident_error_key
                        ierror.save()
                




