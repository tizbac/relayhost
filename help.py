from colors import *
import string
helptext = "Relayed Host Bot\n Documentation is at http://trac.springlobby.info/wiki/HostManagerProtocol"
class Main:
	def oncommandfromserver(self,command,args,socket):
		
		if command == "SAIDPRIVATE" and len(args) > 1 and args[1] == "!help":
			for l in helptext.split("\n"):
				socket.send("SAYPRIVATE %s %s\n" % (args[0],l))
