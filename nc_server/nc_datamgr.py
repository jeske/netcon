#!/neo/opt/bin/python

import time

class NCDataManager:
    def __init__(self,ndb):
        self.ndb = ndb

    # simples way to report data
    #
    #  agent_host  = "c1"
    #
    #  servicepath = "disk/size:total"
    #  source_host = "c4"
    #  source_path = "/dev/sda1"

    #  value       = 24232920


    def handleRawData(self,agent_host,servicepath,source_host,source_path,value):

        # lookup machines

        agent_host_mach = self.ndb.machines.getMachine(agent_host)
        source_host_mach = self.ndb.machines.getMachine(source_host)

        # lookup agent_id

        agent = self.ndb.agents.getAgent(agent_host_mach)

        # lookup service

        service = self.ndb.services.getService(servicepath)

        # lookup source

        source = self.ndb.monitor_sources.getSource(agent,source_host_mach,source_path)

        # add data

        now = int(time.time())
        self.ndb.monitor_state.recordData(service,source,now,value)

        
