from colors import *
from ParseConfig import *
import time
import datetime
class Main:
	sock = 0
	f = 0
	def onload(self,tasc):
		pass
	def oncommandfromserver(self,command,args,socket):
		if command == "SAID" and args[0] == "autohost":
		  self.f.write("[%s] " % (datetime.datetime.fromtimestamp(time.mktime(datetime.datetime.now().timetuple())).ctime()))
		  self.f.write("<%s> %s\n" % ( args[1] , " ".join(args[2:])))
		  self.f.flush()
		if command == "SAIDEX" and args[0] == "autohost":
		  self.f.write("[%s] " % (datetime.datetime.fromtimestamp(time.mktime(datetime.datetime.now().timetuple())).ctime()))
		  self.f.write("* %s %s\n" % ( args[1] , " ".join(args[2:])))
		  self.f.flush()
		if command == "JOINED" and args[0] == "autohost":
		  self.f.write("[%s] " % (datetime.datetime.fromtimestamp(time.mktime(datetime.datetime.now().timetuple())).ctime()))
		  self.f.write("** %s has joined the channel\n" % (args[1]))
		  self.f.flush()
		if command == "LEFT" and args[0] == "autohost":
		  self.f.write("[%s] " % (datetime.datetime.fromtimestamp(time.mktime(datetime.datetime.now().timetuple())).ctime()))
		  self.f.write("** %s has left the channel ( %s )\n" % ( args[1] , " ".join(args[2:])))
		  self.f.flush()
	def onloggedin(self,socket):
		try:
		  self.f.close()
		  
		except:
		  pass
		self.f = open("logs/LOG.txt","aw")
		self.f.write("[%s] " % (datetime.datetime.fromtimestamp(time.mktime(datetime.datetime.now().timetuple())).ctime()))
		self.f.write("********** CONNECTED ***********\n")
		self.f.flush()