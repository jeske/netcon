#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import hdfhelp
import odb


class AdminEditRolePage(NCPage):
    def display(self):
	q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)

	role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
	role.hdfExport("CGI.role", self.ncgi.hdf)

	
	allagents = self.ndb.agents.fetchAllRows()
	for agent in allagents:
	    machine = self.ndb.machines.fetchRow( ('mach_id', agent.mach_id) )
	    agent.hdfExport("CGI.agents.%s" % agent.agent_id,self.ncgi.hdf)
	    machine.hdfExport("CGI.agents.%s.machine" % agent.agent_id,self.ncgi.hdf)

	rolemach = self.ndb.mach_roles.fetchRows( ('role_id', q_role_id) )
	for a_role in rolemach:
	    self.ncgi.hdf.setValue("CGI.mach_roles.%d" % a_role.mach_id,"1")

    def Action_Save(self):
	q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)

	role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
	role.hdfExport("CGI.role", self.ncgi.hdf)

	rolemach = self.ndb.mach_roles.fetchRows( ('role_id', q_role_id) )
	for rm in rolemach:
	    rm.delete()

	mhdf = self.ncgi.hdf.getObj("Query.mach")
	if mhdf and mhdf.child():
	    mhdf = mhdf.child()
	    while mhdf:
		mach_id = int(mhdf.name())

		rm = self.ndb.mach_roles.newRow()
		rm.mach_id = mach_id
		rm.role_id = role.role_id
		rm.save()
		
		mhdf = mhdf.next()

	self.redirectUri("admin_role.py?role_id=%s" % role.role_id)


if __name__ == "__main__":
    context = Context()
    AdminEditRolePage(context, pagename="admin_edit_role_machines").start()



