
import postdata
import time
import string

class NCServerRpc:
    def __init__(self,myhostname):
        self._myhostname = myhostname

        # make sure we can resolve the server hostname!

    def getConfig(self):
	result = postdata.post_multipart("netcon.dotfunk.com",
					 "/netcon/agentCheckIn.py",
					 [('hostname',self._myhostname)],[])
	print result
	config = []

	pos = string.find(result,"CONFIG_DATA_END")
	if pos != -1:
	    config_data = result[:pos]

	    for a_line in string.split(config_data,"\n"):
		a_line = string.strip(a_line)
		if a_line:
		    parts = string.split(a_line)
		    if parts[0] == "CONFIG_DATA":
			if parts[1] != "V1":
			    break
		    else:
			if len(parts) > 1:
			    config.append( (parts[0],parts[1]) )
			else:
			    config.append( (parts[0],"") )
	return config
	

    def checkIn(self,ncmgr):
        now = int(time.time())
        result = postdata.post_multipart("netcon.dotfunk.com","/netcon/agentCheckIn.py",
                            [('hostname',self._myhostname), ('now',str(now))],[('data','data.txt',ncmgr.postdata())])
        print result

                          
        
        
        
