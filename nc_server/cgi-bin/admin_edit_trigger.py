#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import hdfhelp
import string


class AdminEditTriggerPage(NCPage):
    def Action_Save(self):
	error = 0
	q_create = self.ncgi.hdf.getIntValue("Query.create",0)
	
	if q_create:
	    q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)
	    trigger = self.ndb.role_triggers.newRow()
	    trigger.role_id = q_role_id
	else:
	    q_trigger_id = self.ncgi.hdf.getIntValue("Query.trigger_id",-1)
	    trigger = self.ndb.role_triggers.fetchRow( ('trigger_id', q_trigger_id) )

	hdf = self.ncgi.hdf
	
	trigger.name            = hdf.getValue("Query.name","")
	trigger.serv_id         = hdf.getIntValue("Query.serv_id",-1)
	trigger.source_pattern  = hdf.getValue("Query.source_pattern","")
	trigger.level           = hdf.getValue("Query.level","")

	trigger.test_type       = hdf.getValue("Query.test_type","")
	try:
	    trigger.tvalue      = string.atof(hdf.getValue("Query.tvalue","0"))
	except ValueError:
	    error = 1
	    
	trigger.save()
	if error:
	    self.redirectUri("admin_edit_trigger.py?trigger_id=%s" % trigger.trigger_id)
	else:
	    self.redirectUri("admin_role.py?role_id=%s" % trigger.role_id)

    def setup(self):
	
	# export services
	services = self.ndb.services.fetchRows(order_by=['namepath'])
	for a_service in services:
	    a_service.hdfExport("CGI.services.%d" % a_service.serv_id,
				self.ncgi.hdf)

    def display(self):
	hdf = self.ncgi.hdf
	
	q_create = hdf.getIntValue("Query.create",0)


	if q_create:
	    self.display_create()
	else:
	    self.display_edit()

    def display_create(self):
	q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)
	self.ncgi.hdf.setValue("CGI.role_id", str(q_role_id))
	self.ncgi.hdf.setValue("CGI.create","1")


    def display_edit(self):
	q_trigger_id = self.ncgi.hdf.getIntValue("Query.trigger_id",-1)
	
	trigger = self.ndb.role_triggers.fetchRow( ('trigger_id', q_trigger_id) )
	trigger.hdfExport("CGI.trigger", self.ncgi.hdf)

	self.ncgi.hdf.setValue("CGI.role_id",str(trigger.role_id))


	

if __name__ == "__main__":
    context = Context()
    AdminEditTriggerPage(context, pagename="admin_edit_trigger").start()



