
# trigger manager

import string,re
from log import *

import odb

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
        log("runAllTriggers()")

        alltriggers = ndb.role_triggers.fetchAllRows()
        for a_trigger in alltriggers:
            log("run trigger test: %s" % a_trigger.name)

            # identify which machines to apply this trigger to
            machine_ids = ndb.mach_roles.getMachineIdsInRoleId(a_trigger.role_id)

            # idenfity which agents are on those machines
            agent_ids = ndb.agents.fetchAgentIdsForMachineIdList(machine_ids)

            # fetch all sources for these machines
            allsources = ndb.monitor_sources.fetchForAgentIdList(agent_ids)

            # cull out sources which don't match our pattern
	    if string.strip(a_trigger.source_pattern):
		sources = []
		for a_source in allsources:
		    if re.match(a_trigger.source_pattern,a_source.source_name):
                        # print "match: '%s' - '%s'" % (a_trigger.source_pattern,
                        #                               a_source.source_name)
			sources.append(a_source)
	    else:
		sources = allsources
            
            # fetch all current data for these sources and our triggered service
            alldata = []
            for a_source in sources:
                statedata = ndb.monitor_state.fetchRows( [('serv_id', a_trigger.serv_id),
                                                          ('source_id', a_source.source_id)] )
                if not alldata:
                    alldata = statedata
                else:
                    alldata = alldata + statedata

            # process this data and set the trigger state...
	    tester = NCTriggerTest(a_trigger)
	    
            for cdata in alldata:
		# check if data is current!
		if (cdata.pend + 30*60) < time.time():
                    continue
                else:
		    state = tester.checkMatch(cdata.value)

		# now check trend computations

		if not state and a_trigger.trend_config:
		    try:
			unit_mult = { 'd' : 86400, 'h' : 3600, 'm' : 60 }
			t,unit = string.split(a_trigger.trend_config,":")
			t = float(t)
			trend_srv = ndb.services.getService("trigger/%s:seconds" % a_trigger.trigger_id)
			trend_state = ndb.monitor_state.fetchRow(
			    [('serv_id', trend_srv.serv_id),
			     ('source_id', cdata.source_id)])

			log("trend state: %s" % trend_state.value)

			if ( (trend_state.value > 0) and
			     (trend_state.value < (t * unit_mult.get(unit,0))) ):
			    state = 1
			
			
		    except odb.eNoMatchingRows:
			pass
		    except ValueError:
			log("invalid trend_config: %s" % a_trigger.trend_config)
		    


                tsrv = ndb.services.getService("trigger/%s:state" % a_trigger.trigger_id)
                source = ndb.monitor_sources.fetchRow( ('source_id', cdata.source_id) )
                now = cdata.pend
                ndb.monitor_state.recordData(tsrv,source,now,state)

		    


