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
	listfull = False
	bots = dict()
	disabled = False
	def botthread(self,nick,s,r,p,ist):
		try:
			logc(s,"Spawning "+nick)
			d = dict()
			d.update([("serveraddr",self.app.config["serveraddr"])])
			d.update([("serverport",self.app.config["serverport"])])
			d.update([("admins",self.app.config["admins"])])
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
			if len(ist.ul) < len(ist.an) and ist.listfull:
				ist.listfull = False
				s.send("MYSTATUS 0\n")
		except:
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
	def onload(self,tasc):
		self.tsc = tasc
		self.app = tasc.main
		self.an = parselist(self.app.config["accountsnick"],",")
		self.ap = parselist(self.app.config["accountspass"],",")
		self.disabled = bool(int(self.app.config["enabled"]))
	def oncommandfromserver(self,command,args,socket):
		try:
			if command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!enable":
				self.disabled = False
				socket.send("MYSTATUS %i\n" % int(int(self.listfull)+int(self.disabled)*2))
				socket.send("SAYPRIVATE %s %s\n" % (args[0],"Hosting new games enabled"))
				self.app.SaveConfig()
			if command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!disable":
				self.disabled = True
				socket.send("MYSTATUS %i\n" % int(int(self.listfull)+int(self.disabled)*2))
				socket.send("SAYPRIVATE %s %s\n" % (args[0],"Hosting new games disabled"))
				self.app.SaveConfig()
			if command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!spawn" and args[0] not in self.ul and len(self.ul) < len(self.an) and not self.disabled:
				self.threads.append(thread.start_new_thread(self.botthread,(self.an[len(self.ul)],socket,args[0],self.ap[len(self.ul)],self)))
				socket.send("SAYPRIVATE %s %s\n" %(args[0],self.an[len(self.ul)]))
				self.ul.append(args[0])
				if len(self.ul) >= len(self.an):
					self.listfull = True
					socket.send("MYSTATUS 1\n")

			elif command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!spawn" and len(self.ul) >= len(self.an):
				socket.send("SAYPRIVATE %s %s\n" %(args[0],"\001 Error: All bots are spawned"))
			#elif command == "SAIDPRIVATE" and len(args) >= 1 and :
			#	socket.send("SAYPRIVATE %s %s\n" %(args[0],"\002"))
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
		socket.send("MYSTATUS %i\n" % int(int(self.listfull)+int(self.disabled)*2))		
