#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage

import hdfhelp
import odb


class AdminEditConfigPage(NCPage):
    def display(self):
	q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)

	role = self.ndb.roles.fetchRow( ('role_id', q_role_id) )
	role.hdfExport("CGI.role", self.ncgi.hdf)

	# export role config

	rclist = self.ndb.role_config.fetchRows(
	    ('role_id', role.role_id) )
	rclist.hdfExport("CGI.role_config",self.ncgi.hdf)

    def Action_Save(self):
	q_role_id = self.ncgi.hdf.getIntValue("Query.role_id",-1)

	# create new config rows!
	hdf = self.ncgi.hdf.getObj("Query.rows")
	if hdf and hdf.child():
	    hdf = hdf.child()
	    while hdf:
		collector = hdf.getValue("collector","")
		collector_config = hdf.getValue("collector_config","")
		role_config_id = hdf.getIntValue("role_config_id",-1)
		should_delete = hdf.getIntValue("delete",0)
		hdf = hdf.next()

		if role_config_id == -1:
		    if collector or collector_config:
			nrc = self.ndb.role_config.newRow()
			nrc.role_id = q_role_id
		    else:
			continue
		    
		else:
		    try:
			nrc = self.ndb.role_config.fetchRow(
			    ('role_config_id', role_config_id) )
		    except odb.eNoMatchingRows:
			continue

		if should_delete:
		    nrc.delete()
		else:
		    nrc.collector = collector
		    nrc.collector_config = collector_config
		    nrc.save()

	self.redirectUri("admin_role.py?role_id=%s" % q_role_id)
	

if __name__ == "__main__":
    context = Context()
    AdminEditConfigPage(context, pagename="admin_edit_config").start()



