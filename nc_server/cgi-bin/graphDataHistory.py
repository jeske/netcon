#!/neo/opt/bin/python

import tstart

from CSPage import Context, DisplayDone
from nc_page import NCPage

import re,sys
from log import log
import neo_cgi,neo_util

import odb

from PIL import Image, ImageDraw

class GraphImage:
    def __init__(self,width,height):
	self.antialias_factor = 4
	self.width = width * self.antialias_factor
	self.height = height * self.antialias_factor
	self.data = []
	self.max = None
	self.min = None
	self.fixed_vscale = 0

    def addData(self,data):
	self.data.append(data)

	if not self.fixed_vscale:
	    if self.max is None: self.max = data
	    if self.min is None: self.min = data
	    if self.max < data: self.max = data
	    if self.min > data: self.min = data

    def setMinMax(self,min,max):
	self.min = min
	self.max = max
	self.fixed_vscale = 1
	
    def makeImage(self):
	if self.min == self.max:
	    if self.min is None:
		self.min = 0
		self.max = 0
	    else:
		self.min = self.min - 15
		self.max = self.max + 15
        else:
            if (self.max * 2) < self.height:
                self.min = 0
	    
	# vertical scaling
	vscale = (float(self.height) / float(self.max - self.min))
	im = Image.new("RGB",(self.width,self.height),(255,255,255))
	imd = ImageDraw.Draw(im)

	def wideline( imd, linedata, **param):
	    x1,y1,x2,y2 = linedata
	    for x in range(self.antialias_factor):
		imd.line( (x1+x,y1+x,x2+x,y2+x), **param)
		
	curx = 0
	if len(self.data):

	    cury = (self.data[0]-self.min) * vscale
	    if len(self.data) > 1:
		hscale = (float(self.width) / float(len(self.data)-1))
		for dp in self.data[1:]:
		    pos = (dp-self.min) * vscale

		    wideline(imd,((curx*hscale),self.height-cury,
				  ((curx+1)*hscale),self.height-pos) , fill=128)
		    curx = curx + 1
		    cury = pos
	    else:
		hscale = float(self.width)
		wideline(imd,((curx*hscale),self.height-cury,
			      ((curx+1)*hscale),self.height-cury),fill=128)

        
	return im.resize((self.width/self.antialias_factor,self.height/self.antialias_factor),Image.ANTIALIAS)

class GraphDataHistoryPage(NCPage):
    def display(self):
	hdf = self.ncgi.hdf
	q_service_id = hdf.getIntValue("Query.serv_id",-1)
	q_source_id  = hdf.getIntValue("Query.source_id",-1)
	q_width = hdf.getIntValue("Query.width",400)
	q_height = hdf.getIntValue("Query.height",150)

	service = self.ndb.services.fetchRow( ('serv_id', q_service_id) )
	service.hdfExport("CGI.service", self.ncgi.hdf)

	source = self.ndb.monitor_sources.fetchRow(
	    ('source_id', q_source_id) )
	source.hdfExport("CGI.source", self.ncgi.hdf)

	smach = self.ndb.machines.fetchRow(
	    ('mach_id', source.source_mach_id) )
	smach.hdfExport("CGI.source.machine",self.ncgi.hdf)

        h_data = self.ndb.monitor_history.fetchRows(
	    [ ('serv_id', q_service_id),
	      ('source_id', q_source_id)] )

	h_data.hdfExport("CGI.history", self.ncgi.hdf)

	gi = GraphImage(q_width,q_height)

        # setup fixed scaling
	if service.type == "pct":
	    gi.setMinMax(0,100)
        elif service.type == "state":
            gi.setMinMax(0,1)

	for data in h_data:
	    gi.addData(data.value)

	sys.stdout.write("Content-Type: image/png\n\n")
	gi.makeImage().save(sys.stdout,"PNG")

	raise DisplayDone
		
	

if __name__ == "__main__":
    context = Context()
    GraphDataHistoryPage(context, pagename="viewDataHistory").start()



