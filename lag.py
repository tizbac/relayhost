from colors import *
from ParseConfig import *
class Main:
	sock = 0
	app = 0
	def onload(self,tasc):
		self.app = tasc
	def oncommandfromserver(self,command,args,socket):
		if command == "SAIDPRIVATE" and len(args) > 1 and args[1] == "!lag":
			socket.send("SAYPRIVATE %s %s\n" % ( args[0], str((self.app.lpo-self.app.lp)*1000) +" ms"))
	def onloggedin(self,socket):
		pass
			
