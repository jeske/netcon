

import db_netcon
import os

from CSPage import CSPage

class NCPage(CSPage):
    def subclassinit(self):
        cwd = os.getcwd()
        if cwd.find('blong') != -1:
            self.setPaths(["/home/blong/netcon/nc_server/tmpl"])
        else:
            self.setPaths(["/home/jeske/netcon/nc_server/tmpl"])

        self.ndb = db_netcon.netcon_connect()

	if self.ncgi.hdf.getValue("Query.debug","") == "1":
	    self.ncgi.hdf.setValue("page.debug","1")

