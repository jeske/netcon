#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

class ViewMachinePage(NCPage):
    def display(self):
        q_machine = self.ncgi.hdf.getIntValue("Query.mach_id",0)
        if q_machine:

	    # export the services
	    services = self.ndb.services.fetchRows(order_by=['namepath','type'])
	    serv_hash = {}
	    for a_service in services:
		a_service.hdfExport("CGI.services.%d" % a_service.serv_id,self.ncgi.hdf)
		serv_hash[a_service.serv_id] = a_service

	    # export this machine info..
            machine = self.ndb.machines.fetchRow( ('mach_id',q_machine) )
            machine.hdfExport("CGI.machine",self.ncgi.hdf)

	    # fetch the sources
	    sources = self.ndb.monitor_sources.fetchRows( ('source_mach_id',
							   machine.mach_id) )

               

	    fetch_agents = {}
	    for a_source in sources: fetch_agents[a_source.agent_id] = 1

	    # export involved agents
	    for agent_id in fetch_agents.keys():
		agent = self.ndb.agents.fetchRow( ('agent_id', agent_id) )
		agent.hdfExport("CGI.agent.%d" % agent.agent_id,self.ncgi.hdf)
		machine = self.ndb.machines.fetchRow( ('mach_id', agent.mach_id) )
		machine.hdfExport("CGI.agents.%d.mach_id" % agent.agent_id, self.ncgi.hdf)

	    # go through each source and find the data for the source.

	    stn = 0
	    for a_source in sources:
		prefix = "CGI.agents.%d" % (a_source.agent_id)

		# export the current stats for this machine
		statelist = self.ndb.monitor_state.fetchRows( ('source_id',
							       a_source.source_id) )

		for a_state in statelist:
		    stprefix = prefix + ".state.%d" % stn
		    stn = stn + 1
		    self.ncgi.hdf.setValue(prefix + ".services.%d.serv_id" % (a_state.serv_id),str(a_state.serv_id))
		    a_source.hdfExport(prefix + ".services.%d.sources.%d" % (a_state.serv_id,a_state.source_id),self.ncgi.hdf)
		    a_state.hdfExport(prefix + ".services.%d.sources.%d.states.%s" % (a_state.serv_id,a_state.source_id,stn),self.ncgi.hdf)
		    self.ncgi.hdf.setValue(prefix + ".services.%d.sources.%d.states.%s.value" % (a_state.serv_id,a_state.source_id,stn),"%f" % a_state.value)
	    # export services


                


        # load current incidents
        active = self.ndb.incidents.getAllActiveIncidents()

        n = 0
        for incident in active:
            prefix = "CGI.active_incidents.%s" % n
            incident.hdfExport(prefix,self.ncgi.hdf)

            errs = self.ndb.incident_errors.fetchRows( ('incident_id', incident.incident_id) )
            errs.hdfExport(prefix + ".errors", self.ncgi.hdf)


        # load machines
        machines = self.ndb.machines.fetchAllRows()
        machines.hdfExport("CGI.machines", self.ncgi.hdf)
        

if __name__ == "__main__":
    context = Context()
    ViewMachinePage(context, pagename="viewMachine").start()



