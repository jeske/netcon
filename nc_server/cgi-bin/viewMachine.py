#!/usr/bin/env python

import tstart
import string

from CSPage import Context
from nc_page import NCPage

class ViewMachinePage(NCPage):
    def display(self):
        q_machine = self.ncgi.hdf.getIntValue("Query.mach_id",0)
        if q_machine:
            # export roles and triggers
            role_ids = self.ndb.mach_roles.getRoleIdsForMachineId(q_machine)
            if len(role_ids):
                role_ids = map(lambda x: str(x), role_ids)
                roles = self.ndb.roles.fetchRows(where="role_id in (%s)" % string.join(role_ids, ","))
                roles.hdfExport("CGI.roles", self.ncgi.hdf, export_by="role_id")
                triggers = self.ndb.role_triggers.fetchRows(where="role_id in (%s)" % string.join(role_ids, ","))
                triggers.hdfExport("CGI.triggers", self.ncgi.hdf, export_by="trigger_id")

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
		    self.ncgi.hdf.setValue(prefix + ".services.%d.serv_id" % (a_state.serv_id),str(a_state.serv_id))
		    a_source.hdfExport(prefix + ".services.%d.sources.%d" % (a_state.serv_id,a_state.source_id),self.ncgi.hdf)
		    a_state.hdfExport(prefix + ".services.%d.sources.%d.state" % (a_state.serv_id,a_state.source_id),self.ncgi.hdf)

                    def render_time(s):
                        if abs(s) > 365*86400:
                            return "%0.2f years" % (s/365/86400)
                        elif abs(s) > 86400:
                            return "%0.2f days" % (s/86400)
                        elif abs(s) > 3600:
                            return "%0.2f hours" % (s/3600)
                        elif abs(s) > 60:
                            return "%0.2f min" % (s/60)
                        elif abs(s) > 0:
                            return "%0.2f s" % (s)
                        elif abs(s) > 0.001:
                            return "%0.2f ms" % (s * 1000)
                        elif abs(s) > 0.000001:
                            return "%0.2f ns" % (s * 1000000)
                        return "%0.2f s" % (s)

		    if serv_hash[a_state.serv_id].type in ["seconds", "time"]:
			vf = render_time(a_state.value)
		    elif serv_hash[a_state.serv_id].type == "pct":
			vf = "%0.2f%%" % (a_state.value)
		    elif serv_hash[a_state.serv_id].type == "state":
                        if a_state.value: vf = "true"
                        else: vf = "false"
			# vf = "%0.2f%%" % (a_state.value)
		    else:
                        if serv_hash[a_state.serv_id].namepath in ["disk/size", "machine/memory", "mysql/innodb/free"]:
                            # already in K
                            if a_state.value > 1024*1024:
                                vf = "%0.2fGB" % (a_state.value / 1024 / 1024)
                            elif a_state.value > 1024:
                                vf = "%0.2fMB" % (a_state.value / 1024)
                            else:
                                vf = "%dKB" % a_state.value
                        else:
                            if int(a_state.value) != a_state.value:
                                vf = "%0.2f" % a_state.value
                            else:
                                if a_state.value > 1000000:
                                    vf = "%0.2fm" % (a_state.value / 1000000)
                                elif a_state.value > 1000:
                                    vf = "%0.2fk" % (a_state.value / 1000)
                                else:
                                    vf = "%d" % a_state.value

                    if serv_hash[a_state.serv_id].namepath[:8] == "trigger/" \
                       and serv_hash[a_state.serv_id].type == "state":
                        if a_state.value == 1:
                            self.ncgi.hdf.setValue(prefix + ".services.%d.sources.%d.state.value.triggered" % (a_state.serv_id,a_state.source_id),"1")
		    
		    self.ncgi.hdf.setValue(prefix + ".services.%d.sources.%d.state.value" % (a_state.serv_id,a_state.source_id),vf)
	    # export services


        # load current incidents
        active = self.ndb.incidents.getAllActiveIncidents()

        trigger_to_incident = {}
        n = 0
        for incident in active:
            prefix = "CGI.active_incidents.%s" % n
            incident.hdfExport(prefix,self.ncgi.hdf)

            errs = self.ndb.incident_errors.fetchRows( ('incident_id', incident.incident_id) )
            errs.hdfExport(prefix + ".errors", self.ncgi.hdf)
            n = n + 1


        # load machines
        machines = self.ndb.machines.fetchAllRows()
        machines.hdfExport("CGI.machines", self.ncgi.hdf)
        

if __name__ == "__main__":
    context = Context()
    ViewMachinePage(context, pagename="viewMachine").start()



