create table nc_machines (
  mach_id integer not null primary key auto_increment,
  network_parent_id integer default 0,
  name varchar(255),
  ip varchar(255)
) TYPE=INNODB;

create table nc_agents (
  agent_id integer not null primary key auto_increment,
  mach_id integer not null,
  last_check_in integer default 0
) TYPE=INNODB;

create table nc_services (
  serv_id integer not null primary key auto_increment,
  namepath text,
  type varchar(255)
) TYPE=INNODB;

create table nc_monitor_sources (
  source_id integer not null primary key auto_increment,
  agent_id integer not null,
  source_mach_id integer not null,
  source_name varchar(255)
) TYPE=INNODB;

create table nc_monitor_state (
  source_id integer not null,
  pstart integer not null,
  pend   integer not null,
  primary key (source_id,pstart,pend),

  value real
) TYPE=INNODB;

create table nc_monitor_history (
  source_id integer not null,
  pend   integer not null,
  pstart integer not null,
  primary key (source_id,pend,pstart),

  value real

) TYPE=INNODB;

create table nc_roles (
  role_id integer not null primary key auto_increment,
  name varchar(255),
  is_shared integer default 0
) TYPE=INNODB;

create table nc_mach_roles (
  mach_id integer not null,
  role_id integer not null,
  primary key (role_id,mach_id)
) TYPE=INNODB;

create table nc_role_triggers (
  trigger_id integer not null primary key auto_increment,
  role_id integer not null,
  serv_id integer not null,
  source_pattern varchar(255),
  level varchar(255)
) TYPE=INNODB;

create table nc_incidents (
  incident_id integer not null primary key auto_increment,
  start integer not null,
  end integer not null,
  is_active integer not null default 1,
  index (is_active)
  
) TYPE=INNODB;

create table nc_incident_errors (
  incident_error_map_id integer not null primary key auto_increment,
  incident_id integer not null,
  index (incident_id),
  error_spec text

) TYPE=INNODB;

create table nc_incident_event_audit (
  audit_id integer not null primary key auto_increment,
  occured_at integer not null,
  e_type varchar(255),
  e_data text,
  note text
) TYPE=INNODB;
