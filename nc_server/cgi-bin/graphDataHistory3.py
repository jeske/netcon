#!/usr/bin/env python

import tstart

from CSPage import Context, DisplayDone
from nc_page import NCPage

import re,sys,time,math
from log import log
import neo_cgi,neo_util

import odb

from PIL import Image, ImageDraw, ImageFont

import nc_trends

kDayGraph = 0
kWeekGraph = 1
kMonthGraph = 2
kYearGraph = 3

class Point:
  def __init__(self, val, minval, maxval, pstart, pend):
    self.value = val
    self.maxval = maxval
    self.minval = minval
    self.pstart = pstart
    self.pend = pend

class Dataset:
  def __init__(self):
    self.data = []
    
    self.y_max = None
    self.y_min = None

    self.x_max = None
    self.x_min = None

  def addData(self, data):
    self.data.append(data)

    self.y_max = max(self.y_max, data.value)
    if self.y_min is None: self.y_min = data.value
    self.y_min = min(self.y_min, data.value)

    self.x_max = max(self.x_max, data.pend)
    if self.x_min is None: self.x_min = data.pstart
    self.x_min = min(self.x_min, data.pstart)


def figureGraphType(graphType):
  if graphType == kDayGraph:
    xTickRange = 3600
    xMinTicks = 24
    xMinRange = 0
    xDisplayRange = (3600*24)
  elif graphType == kWeekGraph:
    xTickRange = 3600*24
    xMinTicks = 7
    xMinRange = 60*15
    xDisplayRange = (3600*24)*7
  elif graphType == kMonthGraph:
    xDisplayRange = (3600*24)*7*4
    xMinTicks = 4
    xMinRange = 3600*1
    xTickRange = 3600*24*7
  elif graphType == kYearGraph:
    xDisplayRange = (3600*24)*365
    xMinTicks = 12
    xMinRange = 3600*24
    xTickRange = 3600*24*31

  return xTickRange, xMinTicks, xDisplayRange, xMinRange
  

class GraphImage:
    def __init__(self,width,height, graphType):
      self.antialias_factor = 1
      self.width = width * self.antialias_factor
      self.height = height * self.antialias_factor
      self.graphType = graphType

      self.datasets = {}

      self.fixed_vscale = 0
      self.y_min = None
      self.y_max = None

    def addData(self, nset, data):
      try:
	dataset = self.datasets[nset]
      except KeyError:
	dataset = Dataset()
	self.datasets[nset] = dataset

      dataset.addData(data)

    def setMinMax(self,min,max):
	self.y_min = min
	self.y_max = max
	self.fixed_vscale = 1

    def makeImage(self):
	if self.y_min == self.y_max:
	    if self.y_min is None:
		self.y_min = 0
		self.y_max = 0
	    else:
		self.y_min = self.y_min - 15
		self.y_max = self.y_max + 15

	# vertical scaling
	im = Image.new("RGB",(self.width,self.height),(255,255,255))
	imd = ImageDraw.Draw(im)

	top_margin = 30
	bottom_margin = 20
	left_margin = 50
	right_margin = 50

	datasets = self.datasets.values()

	## find the range of the X axis

	x_max = datasets[0].x_max
	x_min = datasets[0].x_min

	for dataset in datasets[1:]:
	  x_max = max(dataset.x_max, x_max)
	  x_min = min(dataset.x_min, x_min)

	xTickRange, xMinTicks, xDisplayRange, xMinRange = figureGraphType(self.graphType)

	maxx = x_max
	minx = x_max - xDisplayRange
	xrange = maxx - minx


	## clip the datasets

	y_max = None
	y_min = None

	clipped_datasets = []

	num_clipped = 0

	for dataset in datasets:
	  data = []
	  clipped_datasets.append(data)
	  for dp in dataset.data:
	    if dp.pend < minx or dp.pstart > maxx:
	      num_clipped = num_clipped + 1
	      pass
	    elif dp.pstart >= minx and dp.pend <= maxx:
	      data.append(dp)
	      y_max = max(dp.value, y_max)
	      if y_min is None: y_min = dp.value
	      y_min = min(dp.value, y_min)

	    else:
	      x1 = max(minx, dp.pstart)
	      x2 = min(maxx, dp.pend)

	      if x1 >= minx and x2 <= maxx:
		if x1 != dp.pstart or x2 != dp.pend:
		  p = Point(dp.value, dp.minval, dp.maxval, x1, x2)
		  data.append(p)
		else:
		  data.append(dp)
	  log("num_clipped=%s" % num_clipped)


        if y_max is None: y_max = 0
        if y_min is None: y_min = 0

	if self.fixed_vscale:
	  y_max = self.y_max
	  y_min = self.y_min

	maxy = math.ceil(y_max)
	miny = math.floor(y_min)
	yrange = maxy-miny

	height = self.height / self.antialias_factor
	width = self.width / self.antialias_factor

	gx1 = left_margin
	gy1 = top_margin
	gx2 = width - right_margin
	gy2 = height - bottom_margin


	num_xticks = int((1.0 * xrange / xTickRange)+1)
	num_xticks = min(xMinTicks, num_xticks)
	tick_x = 1.0 * (gx2-gx1) / num_xticks
	data_tick_x = 1.0 * xrange / num_xticks

	num_yticks = int((gy2-gy1) / 20.)
	tick_y = 1.0 * (gy2-gy1) / num_yticks
	data_tick_y = 1.0 * yrange / num_yticks


	top_marginf = top_margin*self.antialias_factor
	bottom_marginf = bottom_margin*self.antialias_factor
	left_marginf = left_margin*self.antialias_factor
	right_marginf = right_margin*self.antialias_factor

	graph_height = self.height - (top_marginf + bottom_marginf)
	graph_width = self.width - (left_marginf + right_marginf)

        if yrange == 0:
            yscale = 1
        else:
            yscale = (float(graph_height) / float(yrange))
        if xrange == 0:
            xscale = 1
        else:
            xscale = (float(graph_width) / float(xrange))

	def wideline( imd, linedata, **param):
	  for x in range(self.antialias_factor):
	    linedata = map(lambda (_x,_y): (_x+x, _y+x), linedata)
	    imd.line(linedata, **param)


	## clip the data to the X boundaries


	colors = [(0xee, 0xdd, 0x99), (255, 180, 180), (180, 180, 255)]
	linecolors = [(255,0,0), (0,128,128), (0,0, 255)]

	nset = 0
	for data in clipped_datasets:
	  if len(data):
	      lastx = (data[0].pstart-minx) * xscale
	      lasty = (data[0].value-miny) * yscale

	      points = []
	      min_points = []
	      max_points = []


	      for dp in data:
		  pos_y = (dp.value-miny) * yscale

## 		  pos_y_min = (dp.minval-miny) * yscale
## 		  pos_y_max = (dp.maxval-miny) * yscale

		  x1 = (dp.pstart-minx) * xscale
		  x2 = (dp.pend-minx) * xscale

		  y = graph_height-pos_y
##		  y_min = graph_height-pos_y_min
##		  y_max = graph_height-pos_y_max

		  x1 = x1 + left_marginf
		  x2 = x2 + left_marginf
		  y = y + top_marginf
##		  y_min = y_min + top_marginf
##		  y_max = y_max + top_marginf

		  if x1 != x2:
		    points.append((x1, y))
## 		    max_points.append((x1, y_min))
## 		    min_points.append((x1, y_max))

		  points.append((x2, y))
## 		  min_points.append((x2, y_min))
## 		  max_points.append((x2, y_max))

		  lastx = x2
		  lasty = y

	      first_point = points[0]
	      
	      points.append((lastx, graph_height+top_marginf))
	      points.append((first_point[0], graph_height+top_marginf))
	      points.append(first_point)

	      imd.polygon(points, fill=colors[nset])

#	      wideline(imd,min_points, fill=linecolors[nset+1])
#	      wideline(imd,max_points, fill=linecolors[nset+2])
	      wideline(imd,points[:-3], fill=linecolors[nset])


	  nset=nset+1

        
	im = im.resize((width, height),Image.ANTIALIAS)
	imd = ImageDraw.Draw(im)

	grid_im = Image.new("RGB",(width,height),(255,255,255))
	grid_imd = ImageDraw.Draw(grid_im)


	## draw graph border

	imd.line((gx1,gy1,gx1,gy2), fill=0)
	imd.line((gx1,gy2,gx2,gy2), fill=0)
	imd.line((gx2,gy2,gx2,gy1), fill=0)
	imd.line((gx2,gy1,gx1,gy1), fill=0)


	## draw the Y axis grid lines and axis labels

	font = imd.getfont()


	for ty in range(0,num_yticks+1):
	  dy = (tick_y * ty) + gy1
	  imd.line((gx1-2, dy, gx1, dy), fill=0)
	  imd.line((gx2, dy, gx2+2, dy), fill=0)

	  y = (data_tick_y * (num_yticks-ty) + miny)
	  str = "%.1f" % y
	  (sw, sh) = font.getsize(str)
	  imd.text((gx1-sw-10, dy-(sh/2)), str, fill=0)
	  imd.text((gx2+5, dy-(sh/2)), str, fill=0)

	  grid_imd.line((gx1+1, dy, gx2-1, dy), fill=0)


	## draw the X axis grid lines and axis labels

	for tx in range(0,num_xticks+1):
	  dx = (tick_x * tx) + gx1
	  imd.line((dx, gy2, dx, gy2+3), fill=0)

 	  x = (data_tick_x * tx) + minx
 	  t = time.localtime(x)
	  if self.graphType == kDayGraph:
	    str = "%d" % t[3]
	  elif self.graphType == kWeekGraph:
	    wday = time.strftime("%a", t)
	    str = wday
	  elif self.graphType == kMonthGraph:
	    wday = time.strftime("%V", t)
	    str = "Wk #" + wday
	  elif self.graphType == kYearGraph:
	    wday = time.strftime("%b", t)
	    str = wday



 	  (sw, sh) = font.getsize(str)
	  imd.text((dx-(sw/2), gy2+(sh/2)), str, fill=0)

	  grid_imd.line((dx, gy1+1, dx, gy2), fill=0)

#	im2 = im
	im2 = Image.blend(im, grid_im, .1)


	
	return im2

class GraphDataHistoryPage(NCPage):
    def _fetchRows1(self, q_service_id, q_source_id, lasttime):

      rows = self.ndb.monitor_history.fetchRows(
	[ ('serv_id', q_service_id),
	  ('source_id', q_source_id)],
	where='pend >= %s' % lasttime, order_by=['pend desc'])


      return rows

    def _fetchSummaryRows1(self, q_service_id, q_source_id, level, lasttime):
      rows = self.ndb.monitor_summary.fetchRows(
	[ ('serv_id', q_service_id),
	  ('source_id', q_source_id),
	  ('level', level)] ,
	where='pend >= %s' % lasttime, order_by=['pend desc'])

      return rows

    def _fetchSummaryRows2(self, q_service_id, q_source_id, level, lasttime):
      rows = []

      i = 0
      
      incr = 350
      while 1:
	h_data = self.ndb.monitor_summary.fetchRows(
	  [ ('serv_id', q_service_id),
	    ('source_id', q_source_id),
	    ('level', level)] ,
	  skip_to=i, limit_to=incr, order_by=['pend desc'])

	if len(h_data) == 0: break

	rows = rows + h_data
	log("len(rows)=%s" % len(rows))

	if h_data[-1].pstart < lasttime: break

	i = i + incr


      firstTime = rows[0].pend
      
      moreRows = self._fetchRows1(q_service_id, q_source_id, firstTime)
      log("len(moreRows)=%s" % len(moreRows))
      rows = moreRows + rows
      
      return rows



    def display(self):
	hdf = self.ncgi.hdf

	sets = []

	nset = 0
	while 1:
	  q_service_id = hdf.getIntValue("Query.serv_id.%s" % nset,-1)
	  if q_service_id == -1: break
	  q_source_id  = hdf.getIntValue("Query.source_id.%s" % nset,-1)

	  sets.append((nset, q_service_id, q_source_id))
	  nset = nset + 1


	if len(sets) == 0:
	  q_service_id = hdf.getIntValue("Query.serv_id",-1)
	  q_source_id  = hdf.getIntValue("Query.source_id",-1)

	  sets.append((0, q_service_id, q_source_id))

	q_graphType = hdf.getIntValue("Query.graphtype",0)

	q_width = hdf.getIntValue("Query.width",550)
	q_height = hdf.getIntValue("Query.height",150)

	gi = GraphImage(q_width,q_height, q_graphType)

	xTickRange, xMinTicks, xDisplayRange, xMinRange = figureGraphType(q_graphType)

	now = time.time()

	lasttime = int(now - (xDisplayRange))

	for (nset, q_service_id, q_source_id) in sets:

	  startTime = time.time()

	  service = self.ndb.services.fetchRow( ('serv_id', q_service_id) )
	  source = self.ndb.monitor_sources.fetchRow(
	    ('source_id', q_source_id) )

	  smach = self.ndb.machines.fetchRow(
	    ('mach_id', source.source_mach_id) )

	  if xMinRange == 0:
	    h_data = self._fetchRows1(q_service_id, q_source_id, lasttime)
	  else:
	    h_data = self._fetchSummaryRows2(q_service_id, q_source_id, xMinRange, lasttime)

	  h_data.reverse()

	  log("len(h_data)=%s" % len(h_data))

	  endTime = time.time()
	  dt = endTime - startTime
	  log("fetching rows %.2f" % dt)

	  startTime = time.time()

	  incremental = 0
	  # setup fixed scaling
	  if service.type == "pct":
	      gi.setMinMax(0,100)
	  elif service.type == "state":
	      gi.setMinMax(0,1)
	  elif service.type in ("inc", "total"):
	    incremental = 1

	  if incremental:
	    n = h_data[0].value
	    for data in h_data:
	      p = Point(data.value-n, None, None, data.pstart, data.pend)
	      gi.addData(nset, p)
	      n = data.value
	  else:
	    for data in h_data:
	      gi.addData(nset, data)

	  endTime = time.time()
	  dt = endTime - startTime
	  log("generating point set %.2f" % dt)

	sys.stdout.write("Content-Type: image/png\n\n")

	startTime = time.time()

	try:
	  im = gi.makeImage()
	except:
	  import handle_error
	  handle_error.handleException("Error")

	endTime = time.time()
	dt = endTime - startTime
	log("makeImage %.2f" % dt)

	startTime = time.time()

	im.save(sys.stdout,"PNG")

	endTime = time.time()
	dt = endTime - startTime
	log("generating PNG %.2f" % dt)

	raise DisplayDone
		
	

if __name__ == "__main__":
    context = Context()
    GraphDataHistoryPage(context, pagename="viewDataHistory").start()



