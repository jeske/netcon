
# trigger manager


from log import *

class NCTriggerManager:
    def __init__(self,ndb):
        self.ndb = ndb

    def runAllTriggers(self):
        ndb = self.ndb
        # for each trigger, run over "current state" data and see if we have any errors

        alltriggers = ndb.role_triggers.fetchAllRows()
        for a_trigger in alltriggers:

            # identify which machines to apply this trigger to
            machine_ids = ndb.mach_roles.getMachineIdsInRoleId(a_trigger.role_id)

            # fetch all sources for these machines
            sources = ndb.monitor_sources.fetchForMachineIdList(machine_ids)

            # FIXME: cull out sources which don't match our pattern
            
            # fetch all current data for these sources and our triggered service
            alldata = None
            for a_source in sources:
                statedata = ndb.monitor_state.fetchRows( [('serv_id', a_trigger.serv_id),
                                                          ('source_id', a_source.source_id)] )
                if alldata is None:
                    alldata = statedata
                else:
                    alldata = alldata + statedata

            # process this data and set the trigger state...
            for cdata in alldata:
                if cdata.value > 100:
                    state = 1
                    log("%s: data value %s > 100" % (cdata.source_id,cdata.value))
                else:
                    state = 0

                tsrv = ndb.services.getService("trigger/%s:state" % a_trigger.trigger_id)
                source = ndb.monitor_sources.fetchRow( ('source_id', cdata.source_id) )
                now = cdata.pend
                ndb.monitor_state.recordData(tsrv,source,now,state)

