#!/neo/opt/bin/python

import tstart

import db_netcon
import whrandom
import nlregress
import linreg

from Simplex import Simplex

import time

class NCTrends:
    def __init__(self):
	pass

def try_linreg(h_data):
    vals = map(lambda x: [x.pstart,x.value],h_data)

    coeff = linreg.linearRegression(vals,1)
    print coeff

    def lin_f(x,par):
        m,b = par
        return (m*x) + b

    def lin_fsolve(y,par):
	m,b = par
	return (y-b) / m 

    b,m = coeff
    values = m,b

    print 'today: ' , lin_f(time.time(),values)
    print 'next week: ' , lin_f(time.time() + (86400 * 7),values)

    print 'hit 90 at: ', time.asctime(time.localtime(lin_fsolve(90.,values)))
    print 'hit 100 at: ', time.asctime(time.localtime(lin_fsolve(100.,values)))


def try_simplex(h_data):
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
    
    initial = [whrandom.random(),whrandom.random()]

    s = Simplex(simplex_f,initial,
		[whrandom.random(),whrandom.random()])
    values, err, iter = s.minimize()
    print 'args = ', values
    print 'error = ', err
    print 'iterations = ', iter

    def lin_fsolve(y,par):
	m,b = par
	return (y-b) / m # x = (y-b)/m

    # print 'today: ' , lin_f((time.time() - (now-86399))*200,values)
    print 'today: ' , lin_f(time.time(),values)
    print 'next week: ' , lin_f(time.time() + (86400 * 7),values)
    print 'next year: ' , lin_f(time.time() + (86400 * 365),values)

    print 'hit 90 at: ', time.asctime(time.localtime(lin_fsolve(90,values)))
    print 'hit 100 at: ', time.asctime(time.localtime(lin_fsolve(100,values)))


def try_nlregress(h_data):
    def lin_f(x,par):
	m,b = par
	return (m * x) + b  # y = mx + b

    par = [1,0]
    import whrandom
    xvals = map(lambda x: x.pstart,h_data)
    sigma = map(lambda x: 0.0,xvals)
    yvals = map(lambda x: x.value, h_data)

    err,chi,par = nlregress.non_linear_regression(lin_f,xvals,par,yvals)


    print "Error:       ",err
    print "Chi Squared: ",chi
    print "Parameters:  ",par
    

def main():
    ndb = db_netcon.netcon_connect()

    # 0. load data
    # 1. Compute linear interp and stdv
    # 2. is recent/current data within stdv range?
    # 3. if not, shorten time and repeat
    # 4. if yes, compute time to trend target
    
    # -----------------------

    # 0. load data


    h_data = ndb.monitor_history.fetchRows(
	[ ('serv_id', 4),
	  ('source_id', 6)] )

    # 1. Compute linear interp and stdv

    # try_nlregress(h_data)
    try_simplex(h_data)
    try_linreg(h_data)
    
    # 2. is recent/current data within stdv range?
    # 3. if not, shorten time and repeat
    # 4. if yes, compute time to trend target


if __name__ == "__main__":
    main()


    
