#!/neo/opt/bin/python

from odb import *
from log import *
from hdfhelp import HdfRow, HdfItemList
import profiler
import socket

USER = 'root'
PASSWORD = ''
DATABASE = 'netcon'

class NCMachinesTable(Table):
    def _defineRows(self):
        self.d_addColumn("mach_id", kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("network_parent_id", kInteger, default=0)
        self.d_addColumn("name", kVarString, 255, unique=1)
        self.d_addColumn("ip", kVarString,255)

    def getMachine(self,hostname):
        try:
            mach = self.fetchRow( ('name',hostname) )
        except eNoMatchingRows:
            mach = self.newRow()
            mach.name = hostname
            mach.save()

        return mach

class NCAgentsTable(Table):
    def _defineRows(self):
        self.d_addColumn("agent_id", kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("mach_id", kInteger)
        self.d_addColumn("last_check_in", kInteger, int_date=1)

    def getAgent(self, mach_obj):
        agents = self.fetchRows( ('mach_id', mach_obj.mach_id) )
        if agents:
            agent = agents[0]
        else:
            agent = self.newRow()
            agent.mach_id = mach_obj.mach_id
            agent.save()
            
        return agent

class NCServicesTable(Table):
    def _defineRows(self):
        self.d_addColumn("serv_id",kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("namepath", kBigString, unique=1)
        self.d_addColumn("type", kVarString, 255, unique=1)

        # types: total, cur, state, avg, pct

    def getService(self,servicepath):
        namepath,stype = string.split(servicepath,":")
        
        try:
            service = self.fetchRow( [('namepath', namepath), ('type', stype)] )
        except eNoMatchingRows:
            service = self.newRow()
            service.namepath = namepath
            service.type = stype
            service.save()

        return service

    def getMatchingServices(self,prefix_pattern):
        return self.fetchRows( where=["namepath like '%s%%'" % prefix_pattern] )
        

class NCMonitorSourcesTable(Table):
    def _defineRows(self):
        self.d_addColumn("source_id", kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("agent_id", kInteger)
        self.d_addColumn("source_mach_id",kInteger)
        self.d_addColumn("source_name",kVarString,255)

    def fetchForMachineIdList(self,machine_id_list):
        allsources = None
        for mach_id in machine_id_list:
            sources = self.fetchRows( ('source_mach_id', mach_id) )
            if allsources is None:
                allsources = sources
            else:
                allsources = allsources + sources
        return allsources


    def getSource(self,agent_obj,source_mach_obj,source_name):
        sources = self.fetchRows( [('agent_id', agent_obj.agent_id),
                                   ('source_mach_id', source_mach_obj.mach_id),
                                   ('source_name', source_name)] )
        if sources:
            return sources[0]
        else:
            source = self.newRow()
            source.agent_id = agent_obj.agent_id
            source.source_mach_id = source_mach_obj.mach_id
            source.source_name = source_name
            source.save()
            return source

class NCMonitorStateTable(Table):
    def _defineRows(self):
        self.d_addColumn("serv_id", kInteger, primarykey=1)
        self.d_addColumn("source_id", kInteger, primarykey=1)
        self.d_addColumn("pstart", kInteger, int_date=1)
        self.d_addColumn("pend", kInteger, int_date=1)
        self.d_addColumn("value", kInteger)

    def recordData(self,service,source,at_time, value):
        # first get the current value if there is one

        try:
            curdata = self.fetchRow( [('serv_id', service.serv_id),
                                      ('source_id', source.source_id) ] )

            if (curdata.value != value) or ((curdata.pend + 60*10) < at_time):
                self.db.monitor_history.aggregateData(curdata)
                curdata.pstart = at_time
            
        except eNoMatchingRows:
            curdata = self.newRow()
            curdata.pstart = at_time
            curdata.serv_id = service.serv_id
            curdata.source_id = source.source_id

        curdata.value = value    
        curdata.pend = at_time            
        curdata.save()
        
        

class NCMonitorHistoryTable(Table):
    def _defineRows(self):
        self.d_addColumn("serv_id", kInteger, primarykey=1)
        self.d_addColumn("source_id", kInteger, primarykey=1)
        self.d_addColumn("pstart", kInteger, int_date=1, primarykey=1)
        self.d_addColumn("pend", kInteger, int_date=1, primarykey=1)
        self.d_addColumn("value", kInteger)

    def aggregateData(self,monitor_state_obj):
        # fetch the most recent data

        latest_data_list = self.fetchRows( [('serv_id', monitor_state_obj.serv_id),
                         ('source_id', monitor_state_obj.source_id)], order_by = ['pend desc'], limit_to=1)

        if latest_data_list:
            latest_data = latest_data_list[0]

            if (latest_data.pend > monitor_state_obj.pstart):
                log("ignoring overlapping data...")
                log("  history: " + repr(latest_data))
                log("      new: " + repr(monitor_state_obj))
                return

            if ( (latest_data.pstart == monitor_state_obj.pstart) and
                 (latest_data.pend == monitor_state_obj.pend) ):
                log("ignoring duplicate time range...")
                log("  history: " + repr(latest_data))
                log("      new: " + repr(monitor_state_obj))
                return


            if ( (latest_data.value == monitor_state_obj.value) and
                 ((latest_data.pend + 60*20) >= monitor_state_obj.pstart) ):
                 # aggregate the data!
                latest_data.pend = monitor_state_obj.pend
                latest_data.save()
                return
        else:
            log("creating history for data: " + repr(monitor_state_obj))


        # don't extend the old data, create a nw row out of the current state

        new_data = self.newRow()
        new_data.serv_id = monitor_state_obj.serv_id
        new_data.source_id = monitor_state_obj.source_id
        new_data.value = monitor_state_obj.value
        new_data.pstart = monitor_state_obj.pstart
        new_data.pend = monitor_state_obj.pend
        try:
            new_data.save()
        except eDuplicateKey, reason:
            log("aggregateData failed on duplicate key: " + str(reason))
            new_data.discard()
            
    
            
        
class NCRolesTable(Table):
    def _defineRows(self):
        self.d_addColumn("role_id", kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("name", kVarString, 255)
        self.d_addColumn("is_shared", kInteger, default=0)

class NCMachRolesTable(Table):
    def _defineRows(self):
        self.d_addColumn("mach_id", kInteger, primarykey=1)
        self.d_addColumn("role_id", kInteger, primarykey=1)

    def addMachineRole(self,machine_obj,role_obj):
        role = self.newRow()
        role.mach_id = machine_obj.mach_id
        role.role_id = role_obj.role_id
        try:
            role.save()
        except eDuplicateKey:
            role.discard()
            pass

    def getMachineIdsInRoleId(self,role_id):
        machine_ids = []
        for a_row in self.fetchRows( ('role_id', role_id) ):
            machine_ids.append(a_row.mach_id)
        return machine_ids

class NCRoleTriggersTable(Table):
    def _defineRows(self):
        self.d_addColumn("trigger_id", kInteger, primarykey=1, autoincrement=1)
        self.d_addColumn("role_id", kInteger)
        self.d_addColumn("serv_id", kInteger)
        self.d_addColumn("source_pattern", kVarString, 255)
        self.d_addColumn("level", kVarString, 255)

class NCIncidentsTable(Table):
    def _defineRows(self):
        self.d_addColumn("incident_id",kInteger, primarykey=1, autoincrement=1)
        self.d_addColumn("start",kInteger,int_date=1)
        self.d_addColumn("end",kInteger,int_date=1)
        self.d_addColumn("is_active",kInteger,indexed=1)

    def getAllActiveIncidents(self):
        return self.fetchRows( ('is_active', 1) )

    def getActiveIncident(self,create=0,event_time=None):
        incident_list = self.fetchRows( ('is_active', 1),
                                        order_by = ['end desc'], limit_to=1 )

        if event_time is None:
            use_time = int(time.time())
        else:
            use_time = event_time
        
        if incident_list:
            incident = incident_list[0]
            if (incident.end + 30*60) > time.time():
                if event_time and (event_time > incident.end):
                    incident.end = event_time
                    incident.save()
                return incident

        if create:
            new_incident = self.newRow()
            new_incident.start = use_time
            new_incident.end = use_time
            new_incident.is_active=1
            new_incident.save()
            return new_incident

        raise eNoMatchingRows, "no active incident"

class NCIncidentErrorsTable(Table):
    def _defineRows(self):
        self.d_addColumn("incident_error_map_id", kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("incident_id", kInteger, indexed=1)
        self.d_addColumn("error_spec",kVarString,255)

        # we need a better way to point to errors...


    def findActiveError(self,error_spec):
        active_incidents = self.db.incidents.fetchRows( ('is_active', 1) )

        if not active_incidents:
            raise eNoMatchingRows, "no active error matching spec: %s" % error_spec
        
        active_incident_ids = []
        for incident in active_incidents:
            active_incident_ids.append(str(incident.incident_id))
        idlist = string.join(active_incident_ids,",")
        
        active_error_list = self.fetchRows( ('error_spec', error_spec),
                       where = ['incident_id in (%s)' % idlist])

        if active_error_list:
            return active_error_list[0]
        else:
            raise eNoMatchingRows, "no active error matching spec: %s" % error_spec
        

class NCIncidentEventAuditTable(Table):
    def _defineRows(self):
        self.d_addColumn("audit_id", kInteger, primarykey=1,autoincrement=1)
        self.d_addColumn("occured_at", kInteger, int_date=1)
        self.d_addColumn("e_type", kVarString,255)
        self.d_addColumn("e_data", kBigString)
        self.d_addColumn("note", kBigString)
        
class DB(Database):
    def __init__(self, db, debug=0):
        Database.__init__(self,db)
	self.db = db
        self._cursor = None
        self.debug = debug


        self.machines = NCMachinesTable(self,"nc_machines")
        self.agents = NCAgentsTable(self,"nc_agents")
        self.services = NCServicesTable(self,"nc_services")

        self.monitor_sources = NCMonitorSourcesTable(self,"nc_monitor_sources")
        self.monitor_state   = NCMonitorStateTable(self,"nc_monitor_state")
        self.monitor_history = NCMonitorHistoryTable(self,"nc_monitor_history")

        self.roles = NCRolesTable(self,"nc_roles")
        self.mach_roles = NCMachRolesTable(self,"nc_mach_roles")
        self.role_triggers = NCRoleTriggersTable(self,"nc_role_triggers")

        self.incidents = NCIncidentsTable(self,"nc_incidents")
        self.incident_errors = NCIncidentErrorsTable(self,"nc_incident_errors")
        self.incident_event_audit = NCIncidentEventAuditTable(self,"nc_incident_event_audit")

    def defaultRowClass(self):
        return HdfRow
    def defaultRowListClass(self):
	return HdfItemList

        
    def defaultCursor(self):
        # share one cursor for this db object!
        if self._cursor is None:
            if self.debug:
                self._cursor = profiler.ProfilerCursor(self.db.cursor())
            else:
                self._cursor = self.db.cursor()

        return self._cursor

def netcon_connect(host = 'localhost', debug=0):
    # try to optimize connection if on this machine
    if host != 'localhost':
        local_name = socket.gethostname()
        if string.find(local_name, '.') == -1:
            local_name = local_name + ".neotonic.com"
        if local_name == host:
            host = 'localhost'

    if debug: p = profiler.Profiler("SQL", "Connect -- %s:trans" % (host))
    db = MySQLdb.connect(host = host, user=USER, passwd = PASSWORD, db=DATABASE)
    if debug: p.end()

    retval = DB(db, debug=debug)
    return retval
