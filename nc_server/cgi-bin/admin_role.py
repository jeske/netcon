#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import hdfhelp


class AdminRolePage(NCPage):
    def display(self):
	q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)
	
	role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
	role.hdfExport("CGI.role", self.ncgi.hdf)

	# export services
	services = self.ndb.services.fetchAllRows()
	for a_service in services:
	    a_service.hdfExport("CGI.services.%d" % a_service.serv_id,
				self.ncgi.hdf)

	# export role config

	rclist = self.ndb.role_config.fetchRows(
	    ('role_id', role.role_id) )
	rclist.hdfExport("CGI.role_config",self.ncgi.hdf)

	# fetch machines in role...
	rm_map = self.ndb.mach_roles.fetchRows(
	    ('role_id', role.role_id ) )
	machines = hdfhelp.HdfItemList()
	for rm in rm_map:
	    machine = self.ndb.machines.fetchRow( ('mach_id', rm.mach_id) )
	    machines.append(machine)
	    
	machines.hdfExport("CGI.role_machines",self.ncgi.hdf)


	# fetch triggers in role...
	triggers = self.ndb.role_triggers.fetchRows( ('role_id', role.role_id) ,
                      order_by=['level'])
	triggers.hdfExport("CGI.role_triggers", self.ncgi.hdf)
	

if __name__ == "__main__":
    context = Context()
    AdminRolePage(context, pagename="admin_role").start()



