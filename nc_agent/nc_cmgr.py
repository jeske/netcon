
#
# This is the client side data-collection manager...
#

import string
import re, time

from log import *

class NCCollectionManager:
    def __init__(self,myhostname):
        self._data = []
        self._myhostname = myhostname

    def newData(self,service_name,source_name,value,hostname=None):
        if type(value) == type(""):
            m = re.match("\+?(-?[0-9.]+)[%]?",value)

            try:
                if m:
                    value = float(m.group(1))
                else:
                    raise ValueError, "invalid numeric value: %s" % str(value)
            except ValueError,reason:
                log("NCCollectionManager.newData() error: %s" % reason)
        else:
            value = float(value)

        if (hostname is None) or (hostname=="localhost"):
            hostname = self._myhostname

        self._data.append( (int(time.time()), service_name,hostname, source_name,value) )

    def report(self):
        for a_line in self._data:
            print repr(a_line)

    # create the data for posting to the server
    def postdata(self):
        lines = []
        for d in self._data:
            lines.append(string.join(map(lambda x:str(x),d)," "))

        return string.join(lines,"\n")
  
    
