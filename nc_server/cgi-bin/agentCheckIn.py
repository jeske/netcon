#!/neo/opt/bin/python

import tstart

import string

from CSPage import Context
from nc_page import NCPage

import nc_datamgr


class AgentCheckInPage(NCPage):
    def display(self):
        pathname = self.ncgi.hdf.getValue("Query.data","")
        if pathname:
            # handle the file upload...
            data = self.handle_upload("data")
            self.ncgi.hdf.setValue("CGI.data",data)

            self.parse_data(data)

    def handle_upload(self, varname):
        pathname = self.ncgi.hdf.getValue("Query.%s" % varname,"")
        c_type   = self.ncgi.hdf.getValue("Query.%s.Type" % varname,"")

        if pathname[1] == ":" or pathname[:2] == '\\\\':
            # windows file!
            filename = string.split(pathname,"\\")[-1]
        else:
            filename = string.split(pathname,"/")[-1]

        ul_data = self.ncgi.filehandle(varname).read(6*1024*1024)
        if len(ul_data) > 5 * 1024 * 1024:
            self.ncgi.hdf.setValue("CGI.Upload.ErrorTooBig", "1")
            self.ncgi.hdf.setValue("CGI.file.name", filename)
            len_str = "%5.2f" % (len(ul_data) / 1048576.0)
            self.ncgi.hdf.setValue("CGI.file.length", len_str)
            return

        return ul_data

    # the lines look like this:
    # 
    # 1061359721 disk/inodes:total c1 sda6 2820957.0
    # <time> <service> <source host> <source> <value>

    def parse_data(self,data):
        datamanager = nc_datamgr.NCDataManager(self.ndb)

        record_host = self.ncgi.hdf.getValue("Query.hostname","unknown")
        
        lines = string.split(data,"\n")
        for a_line in lines:
            a_line = string.strip(a_line)
            at,service,source_host,source,value = string.split(a_line," ")

            # add some new data
            datamanager.handleRawData(record_host,service,source_host,source,value,at=at)

            


if __name__ == "__main__":
    context = Context()
    AgentCheckInPage(context, pagename="agentCheckIn").start()



