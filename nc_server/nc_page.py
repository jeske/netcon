

import db_netcon

from CSPage import CSPage

class NCPage(CSPage):
    def subclassinit(self):
        self.setPaths(["/home/jeske/netcon/nc_server/tmpl"])

        self.ndb = db_netcon.netcon_connect()

        self.ncgi.hdf.setValue("page.debug","1")

