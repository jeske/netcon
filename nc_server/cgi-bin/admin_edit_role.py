#!/usr/bin/env python

import tstart

from CSPage import Context
from nc_page import NCPage

import hdfhelp
import odb


class AdminEditRolePage(NCPage):
    def display(self):
	q_create = self.ncgi.hdf.getIntValue("Query.create",0)
	if q_create:
	    self.ncgi.hdf.setValue("CGI.create","1")
	else:
	    q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)

	    role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
	    role.hdfExport("CGI.role", self.ncgi.hdf)
    def Action_Save(self):
	q_create = self.ncgi.hdf.getIntValue("Query.create",0)
	
	if q_create:
	    role = self.ndb.roles.newRow()
	else:
	    q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)
	    role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )

	role.name = self.ncgi.hdf.getValue("Query.name","")
	role.save()
	self.redirectUri("admin_role.py?role_id=%s" % role.role_id)


if __name__ == "__main__":
    context = Context()
    AdminEditRolePage(context, pagename="admin_edit_role").start()



