#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage


class IndexPage(NCPage):
    def display(self):
        # load current incidents
        active = self.ndb.incidents.getAllActiveIncidents()

        n = 0
        for incident in active:
            prefix = "CGI.active_incidents.%s" % n
            incident.hdfExport(prefix,self.ncgi.hdf)

            errs = self.ndb.incident_errors.fetchRows( ('incident_id', incident.incident_id) )
            errs.hdfExport(prefix + ".errors", self.ncgi.hdf)


        # load machines
        machines = self.ndb.machines.fetchAllRows()
        machines.hdfExport("CGI.machines", self.ncgi.hdf)
        

if __name__ == "__main__":
    context = Context()
    IndexPage(context, pagename="index").start()



