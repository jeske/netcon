#!/neo/opt/bin/python

import tstart

from log import *
import time
import db_netcon

import whrandom
import nc_datamgr, nc_triggermgr, nc_incidentmgr

class NCSrv:
    def __init__(self):
        # connect
        self.ndb = db_netcon.netcon_connect()

    def run_triggers(self):
        ndb = self.ndb

        triggermanager = nc_triggermgr.NCTriggerManager(ndb)
        triggermanager.runAllTriggers()
        
    def run_incident_management(self):
        ndb = self.ndb

        incidentmanager = nc_incidentmgr.NCIncidentManager(ndb)
        incidentmanager.updateIncidents()
        
    def run_notification(self):
        ndb = self.ndb

    def run(self):
        self.run_triggers()  # run triggers and generate errors..

        self.run_incident_management() # coalesc errors into incidents

        self.run_notification() # check current incidents and generate notifications

def main():
    ncsrv = NCSrv()
    ncsrv.run()

if __name__ == "__main__":
    main()
