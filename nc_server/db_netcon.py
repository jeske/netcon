#!/neo/opt/bin/python

from odb import *
from log import *
from hdfhelp import HdfRow, HdfItemList
import profiler
import socket

import neo_cgi,neo_util

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
        self.d_addColumn("value", kReal)

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
        self.d_addColumn("value", kReal)

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

class NCRoleConfigTable(Table):
    def _defineRows(self):
	self.d_addColumn("role_config_id", kInteger,
			 primarykey=1, autoincrement=1)
	self.d_addColumn("role_id", kInteger)
	self.d_addColumn("collector", kVarString, 255)
	self.d_addColumn("collector_config", kVarString, 255)

class NCRoleTriggerRow(HdfRow):
    def hdfExport(self,prefix,hdf,**x):
	HdfRow.hdfExport(self,prefix,hdf,**x)
	try:
	    time,unit = string.split(self.trend_config,":")
	    hdf.setValue(prefix + ".trend_config.time",time)
	    hdf.setValue(prefix + ".trend_config.unit",unit)
	except ValueError:
	    pass

class NCRoleTriggersTable(Table):
    def _defineRows(self):
        self.d_addColumn("trigger_id", kInteger, primarykey=1, autoincrement=1)
	self.d_addColumn("name",kVarString,255)
        self.d_addColumn("role_id", kInteger)
        self.d_addColumn("serv_id", kInteger)
        self.d_addColumn("source_pattern", kVarString, 255)
        self.d_addColumn("level", kVarString, 255)

	self.d_addColumn("test_type", kVarString,255)
	self.d_addColumn("trend_config", kVarString, 255)
	self.d_addColumn("tvalue", kReal)
	

kStateNew = 0
kStateViewed = 1
kStateWatched = 2
kStateAck = 3
kStateResolved = 4
kState_enum = { 
    kStateNew : "new",
    kStateViewed : "viewed",
    kStateWatched : "watched",
    kStateAck : "ack",
    kStateResolved : "resolved" }


class NCIncidentRow(HdfRow):
    def getErrors(self):
	return self._table.db.incident_errors.fetchRows( ('incident_id', self.incident_id) )

class NCIncidentsTable(Table):
    def _defineRows(self):
        self.d_addColumn("incident_id",kInteger, primarykey=1, autoincrement=1)
        self.d_addColumn("start",kInteger,int_date=1)
        self.d_addColumn("end",kInteger,int_date=1)
        self.d_addColumn("is_active",kInteger,indexed=1)
	self.d_addColumn("name",kVarString,255)
	self.d_addColumn("state",kInteger, default=0,
			 enum_values=kState_enum)
	self.d_addColumn("until",kInteger, int_date=1) # 0 = none

    def _appendToWhere(self):
	return 'state in (%s)' % string.join(map(lambda x:str(x),[kStateNew,kStateViewed]),",")
    def _activeWhere(self):
	return 'state in (%s)' % string.join(map(lambda x:str(x),[kStateNew,kStateViewed, kStateAck]),",")

    def getIncidentsForNotification(self):
        return self.fetchRows(
	    ('is_active', 1),
	    where=[self._activeWhere()])

    def getAllActiveIncidents(self):
        return self.fetchRows( ('is_active', 1) )

    def getActiveIncident(self,create=0,event_time=None):
        incident_list = self.fetchRows(
	    ('is_active', 1), order_by = ['end desc'], limit_to=1,
	    where=[self._appendToWhere()])

        if event_time is None:
            use_time = int(time.time())
        else:
            use_time = event_time
        
        if incident_list:
            incident = incident_list[0]
            if (incident.end + (30*60)) > time.time():
                if event_time and (event_time > incident.end):
                    incident.end = event_time
                    incident.save()
                return incident
	else:
	    log("empty incident list!")

        if create:
            new_incident = self.newRow()
            new_incident.start = use_time
            new_incident.end = int(time.time())
            new_incident.is_active=1
            new_incident.save()
	    log("created incident: %d" % new_incident.incident_id)
            return new_incident

        raise eNoMatchingRows, "no active incident"


class NCIncidentErrorRow(HdfRow):

    def unpackErrorInfo(self):
	# unpack error info
	ehdf = neo_util.HDF()
	ehdf.readString(self.error_spec)

	# these values should be contained!
	trigger_id = ehdf.getIntValue("trigger_id",-1)
	source_id = ehdf.getIntValue("source",-1)
	trigger_serv_id = ehdf.getIntValue("trigger_serv_id",-1)
	
	return ehdf

    def getSourceRow(self):
	ehdf = self.unpackErrorInfo()
	source_id = ehdf.getIntValue("source",-1)
	
	tsrc = self._table.db.monitor_sources.fetchRow(
	    ('source_id', source_id) )

	return tsrc
	
    def getSourceStateRow(self):
	ehdf = self.unpackErrorInfo()
	source_id = ehdf.getIntValue("source",-1)

	trig = self.getTriggerRow()
	
	cdata = self._table.db.monitor_state.fetchRow(
	    [ ('source_id', source_id ),
	      ('serv_id', trig.serv_id ) ] )
	return cdata
	

    def getTriggerRow(self):
	ehdf = self.unpackErrorInfo()
	# load trigger details
	trigger_id = ehdf.getIntValue("trigger_id",-1)
	trig = self._table.db.role_triggers.fetchRow(
	    ('trigger_id', trigger_id) )
	return trig
    
    def getStateRow(self):
	ehdf = self.unpackErrorInfo()
	trigger_id = ehdf.getIntValue("trigger_id",-1)
	source_id = ehdf.getIntValue("source",-1)

	# load service 
	tsrc = self._table.db.services.getService("trigger/%s:state" % trigger_id)
	# now load the trigger state
	tdata = self._table.db.monitor_state.fetchRow(
	    [ ('source_id', source_id),
	      ('serv_id', tsrc.serv_id) ])

	return tdata

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
	self.d_addColumn("incident_id", kInteger)
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
        self.role_triggers = NCRoleTriggersTable(self,"nc_role_triggers",
						 rowClass=NCRoleTriggerRow)
	self.role_config = NCRoleConfigTable(self,"nc_role_config")

        self.incidents = NCIncidentsTable(self,"nc_incidents",rowClass=NCIncidentRow)
        self.incident_errors = NCIncidentErrorsTable(self,"nc_incident_errors",
						     rowClass=NCIncidentErrorRow)
        self.incident_event_audit = NCIncidentEventAuditTable(self,
							      "nc_incident_event_audit")

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
