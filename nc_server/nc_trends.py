#!/neo/opt/bin/python

import tstart

import linreg
from Simplex import Simplex

import time

import db_netcon
import random

from log import *

class NCTrendsManager:
    def __init__(self,ndb):
	self.ndb = ndb

    def computeTrendTime(self,serv_id,source_id,target):
	h_data = self.ndb.monitor_history.fetchRows(
	    [ ('serv_id', serv_id),
	      ('source_id', source_id)] )

	now = time.time()
	# vals = map(lambda x: ((x.pstart - (now-86400))*200,x.value),h_data)
	vals = map(lambda x: (x.pstart,x.value),h_data)

	def lin_f(x,par):
	    m,b = par
	    return (m * x) + b  # y = mx + b

	def simplex_f(args):
	    err = 0.0
	    for x,y in vals:
		res = abs(lin_f(x,args) - y)
		err = err + res
	    return err

	# m = (y-b) / x
	i_b = 0
	i_x,i_y = vals[0]
	i_m = (i_y-i_b)/i_x
	initial = [ i_m, i_b ]

	initial = [random.random(),random.random()]

	s = Simplex(simplex_f,initial,
		    [random.random(),random.random()])
	values, err, iter = s.minimize()
	log('args = ' + repr(values))
	log('error = ' + repr(err))
	log('iterations = ' + repr(iter))

	def lin_fsolve(y,par):
	    m,b = par
	    return (y-b) / m # x = (y-b)/m

	at = lin_fsolve(float(target),values)
	time_to_target = at - time.time()
	log("time_to_target: " + str(time_to_target))
	return time_to_target
	

    def computeTrendTime_linreg(self,serv_id,source_id,target):
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
        time_to_target = (at - time.time())
        log("time_to_target = " + str(time_to_target))
	return time_to_target

    def computeAllTrends(self):

	# find all disk/size:pct entries

	service = self.ndb.services.getService("disk/size:pct")
	t_service = self.ndb.services.getService("disk/size/to90pct:seconds")

	sources = self.ndb.monitor_state.fetchRows( ('serv_id', service.serv_id) )

	for a_source in sources:
	    seconds = self.computeTrendTime(service.serv_id,a_source.source_id,90)
	    self.ndb.monitor_state.recordData(t_service,a_source,time.time(),seconds)
