#!/usr/bin/env python

import tstart

from CSPage import Context
from nc_page import NCPage

import hdfhelp
import odb


class AdminDeleteRolePage(NCPage):
    def display(self):
      q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)

      role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
      role.hdfExport("CGI.role", self.ncgi.hdf)

    def Action_Cancel(self):
      q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)
      self.redirectUri("admin_role.py?role_id=%s" % q_role_id)

    def Action_Delete(self):
      q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)
      if q_role_id != -1:
	role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
	role.delete()

      self.redirectUri("admin.py")


if __name__ == "__main__":
    context = Context()
    AdminDeleteRolePage(context, pagename="admin_delete_role").start()



