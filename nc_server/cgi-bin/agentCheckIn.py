#!/neo/opt/bin/python

import tstart

from CSPage import Context
from nc_page import NCPage


class AgentCheckInPage(NCPage):
    def display(self):
	pass

if __name__ == "__main__":
    context = Context()
    AgentCheckInPage(context, pagename="agentCheckIn").start()



