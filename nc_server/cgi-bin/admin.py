#!/usr/bin/env python

import tstart

from CSPage import Context
from nc_page import NCPage


class AdminPage(NCPage):
    def display(self):
	roles = self.ndb.roles.fetchAllRows()
	n = 0
	for a_role in roles:
	    prefix = "CGI.roles.%d" % n
	    n = n + 1
	    machines = self.ndb.mach_roles.fetchRows(
		('role_id', a_role.role_id ) )
	    a_role.hdfExport(prefix,self.ncgi.hdf)
	    self.ncgi.hdf.setValue(prefix + ".machine_count",str(len(machines)))
	

if __name__ == "__main__":
    context = Context()
    AdminPage(context, pagename="admin").start()



