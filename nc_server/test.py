#!/neo/opt/bin/python

import tstart

from log import *
import time
import db_netcon

import whrandom
import nc_datamgr, nc_triggermgr, nc_incidentmgr

class TestNetcon:
    def __init__(self):
        # connect
        self.ndb = db_netcon.netcon_connect()


    def test_setup(self):
        ndb = self.ndb
        # feed in machines
        t1 = ndb.machines.getMachine("t1")
        t4 = ndb.machines.getMachine("t4")
        t5 = ndb.machines.getMachine("t5")

        # set machine roles...
        allroles = ndb.roles.fetchAllRows()
        if not allroles:
            role = ndb.roles.newRow()
            role.name = "testrole"
            role.is_shared=1
            role.save()

            allroles = [role]

        for a_role in allroles:
            ndb.mach_roles.addMachineRole(t1,a_role)
            ndb.mach_roles.addMachineRole(t4,a_role)
            ndb.mach_roles.addMachineRole(t5,a_role)

            # create role triggers
            cur_triggers = ndb.role_triggers.fetchRows( ('role_id', a_role.role_id) )
            if not cur_triggers:
                ntrigger = ndb.role_triggers.newRow()
                ntrigger.role_id = a_role.role_id
                serv_for_trig = ndb.services.getService("disk/size:cur")
                log("serv_for_trig: %s" % serv_for_trig.serv_id)
                ntrigger.serv_id = serv_for_trig.serv_id
                ntrigger.level = "1"
                ntrigger.source_pattern = "sda1"
                ntrigger.save()


    def test_addData(self):
        ndb = self.ndb
        datamanager = nc_datamgr.NCDataManager(ndb)    

        # add some new data
        datamanager.handleRawData("t1","disk/size:total","t4","sda1",24232920)

        datamanager.handleRawData("t1","disk/size:cur","t4","sda1",100)
        datamanager.handleRawData("t1","disk/size:cur","t4","sda1",200)

        curdisk = [1,1,1,1,1,1,1,1,1,1,1,5,5]
        datamanager.handleRawData("t5","disk/size:cur","t5","sda1",whrandom.choice(curdisk))

    def test_triggers(self):
        ndb = self.ndb

        triggermanager = nc_triggermgr.NCTriggerManager(ndb)
        triggermanager.runAllTriggers()
        
    def test_incident_management(self):
        ndb = self.ndb

        incidentmanager = nc_incidentmgr.NCIncidentManager(ndb)
        incidentmanager.updateIncidents()
        
    def test_notification(self):
        ndb = self.ndb

    def test(self):
        self.test_setup()
        
        self.test_addData()   # agent checkin

        self.test_triggers()  # run triggers and generate errors..

        self.test_incident_management() # coalesc errors into incidents

        self.test_notification() # check current incidents and generate notifications

def main():
    tnc = TestNetcon()
    tnc.test()
    

if __name__ == "__main__":
    main()
