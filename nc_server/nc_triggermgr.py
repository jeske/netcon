
# trigger manager


from log import *

class NCTriggerTest:
    def __init__(self,a_trigger):
	self._test_type = a_trigger.test_type
	self._tvalue    = float(a_trigger.tvalue)

	if not self._test_type in ['lte','lt','eq','gt','gte']:
	    log("unknown test type: '%s' on trigger:%s" %
		(self._test_type, a_trigger.trigger_id))
	
    def checkMatch(self,value):
	value = float(value)
	if self._test_type == "lte":
	    return value <= self._tvalue
	elif self._test_type == "lt":
	    return value < self._tvalue
	elif self._test_type == "eq":
	    return value == self._tvalue
	elif self._test_type == "gt":
	    return value > self._tvalue
	elif self._test_type == "gte":
	    return value >= self._tvalue
	else:
	    raise "unknown test type!"

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
	    tester = NCTriggerTest(a_trigger)
	    
            for cdata in alldata:
		state = tester.checkMatch(cdata.value)

                tsrv = ndb.services.getService("trigger/%s:state" % a_trigger.trigger_id)
                source = ndb.monitor_sources.fetchRow( ('source_id', cdata.source_id) )
                now = cdata.pend
                ndb.monitor_state.recordData(tsrv,source,now,state)



