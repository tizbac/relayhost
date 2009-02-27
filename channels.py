from colors import *
from ParseConfig import *
class Main:
	sock = 0
	def onload(self,tasc):
		pass
	def oncommandfromserver(self,command,args,socket):
		pass
	def onloggedin(self,socket):
		socket.send("JOIN autohost\n")		
