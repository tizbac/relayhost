from colors import *
from ParseConfig import *
import commands
import thread
import os
import sys
import signal
import traceback
import subprocess
def logc(s,m):
	s.send("SAY autohost %s\n" % m)
def loge(s,m):
	s.send("SAYEX autohost %s\n" % m)
class Main:
	ul = []
	bots = dict()
	def botthread(self,nick,s,r,p):
		try:
			logc(s,"Spawning "+nick)
			d = dict()
			d.update([("serveraddr",self.app.config["serveraddr"])])
			d.update([("serverport",self.app.config["serverport"])])
			d.update([("nick",nick)])
			d.update([("password",p)])
			d.update([("hostport",parselist(self.app.config["hostports"],",")[len(self.ul)-1])])
			d.update([("ahport",parselist(self.app.config["ahports"],",")[len(self.ul)-1])])
			d.update([("plugins","channels,autohost,help")])
			writeconfigfile(nick+".cfg",d)
			p = subprocess.Popen(("python","Main.py","-c", "%s" % (nick+".cfg")),stdout=sys.stdout)
			self.bots.update([(nick,p.pid)])
			print self.bots
			p.wait()
			logc(s,"Destroying "+nick)
			self.ul.remove(r)
		except:
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
	def onload(self,tasc):
		self.app = tasc.main
	def oncommandfromserver(self,command,args,socket):
		try:
			an = parselist(self.app.config["accountsnick"],",")
			ap = parselist(self.app.config["accountspass"],",")
			if command == "SAIDPRIVATE" and args[1] == "!spawn" and args[0] not in self.ul and len(self.ul) < len(an):
				thread.start_new_thread(self.botthread,(an[len(self.ul)],socket,args[0],ap[len(self.ul)]))
				socket.send("SAYPRIVATE %s %s\n" %(args[0],an[len(self.ul)]))
				self.ul.append(args[0])
			elif command == "SAIDPRIVATE" and len(self.ul) >= len(an):
				socket.send("SAYPRIVATE %s %s\n" %(args[0],"\001 Error: All bots are spawned"))
			elif command == "SAIDPRIVATE":
				socket.send("SAYPRIVATE %s %s\n" %(args[0],"\002"))
			elif command == "LEFT" and args[0] == "autohost" and len(args) > 4 and args[3] == "inconsistent" and args[1] in self.bots:
				logc(socket,"Bot(%s) kicked by inconsistent data error , killing" % args[1])
				try:
					os.kill(self.bots[args[1]],signal.SIGKILL)
				except:
					pass
		except:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			loge(socket,"*** EXCEPTION: BEGIN")
			for line in exc:
				loge(socket,line)
			loge(socket,"*** EXCEPTION: END")
	def onloggedin(self,socket):
		pass		
