#!/neo/opt/bin/python

import tstart

import linreg

import time

import db_netcon
from log import *

class NCTrendsManager:
    def __init__(self,ndb):
	self.ndb = ndb

    def computeTrendTime(self,serv_id,source_id,target):
	# 0. load data

	h_data = self.ndb.monitor_history.fetchRows(
	    [ ('serv_id', serv_id),
	      ('source_id', source_id)] )

	vals = map(lambda x: [x.pstart,x.value],h_data)
	    
	coeff = linreg.linearRegression(vals,1)
	log("linreg coeff = " + repr(coeff))

	def lin_f(x,par):
	    m,b = par
	    return (m*x) + b

	def lin_fsolve(y,par):
	    m,b = par
	    return (y-b) / m 

	b,m = coeff
	values = m,b

	at = lin_fsolve(float(target),values)
	return (at-time.time())

    def computeAllTrends(self):

	# find all disk/size:pct entries

	service = self.ndb.services.getService("disk/size:pct")
	t_service = self.ndb.services.getService("disk/size/to90pct:seconds")

	sources = self.ndb.monitor_state.fetchRows( ('serv_id', service.serv_id) )

	for a_source in sources:
	    seconds = self.computeTrendTime(service.serv_id,a_source.source_id,90)
	    self.ndb.monitor_state.recordData(t_service,a_source,time.time(),seconds)
