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
	try:
		s.send("SAY autohost %s\n" % m)
	except:
		pass
def loge(s,m):
	try:
		s.send("SAYEX autohost %s\n" % m)
	except:
		pass
class Main:
	ul = []
	listfull = False
	bots = dict()
	disabled = False
	botstatus = dict()
	def botthread(self,slot,nick,s,r,p,ist):
		try:
			logc(s,"Spawning (Requested by %s) " % r +nick)
			d = dict()
			d.update([("serveraddr",self.app.config["serveraddr"])])
			d.update([("spawnedby",r)])
			d.update([("serverport",self.app.config["serverport"])])
			d.update([("springdedpath",self.app.config["springdedpath"])])
			d.update([("admins",self.app.config["admins"])])
			d.update([("nick",nick)])
			d.update([("password",p)])
			d.update([("hostport",parselist(self.app.config["hostports"],",")[slot])])
			d.update([("ahport",parselist(self.app.config["ahports"],",")[slot])])
			d.update([("plugins","channels,autohost,help")])
			writeconfigfile(nick+".cfg",d)
			p = subprocess.Popen(("python","Main.py","-c", "%s" % (nick+".cfg")),stdout=sys.stdout)
			self.bots.update([(nick,p.pid)])
			#print self.bots
			p.wait()
			logc(s,"Destroying "+nick)
			self.ul.remove(r)
			
			if ist.listfull:
				ist.listfull = False
				ist.updatestatus(s)
			ist.botstatus[slot] = False
		except:
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
	def onload(self,tasc):
		self.tsc = tasc
		self.bans = []
		self.config = readconfigfile("Manager.conf")
		self.bans = parselist(self.config["bans"],",")
		self.app = tasc.main
		self.an = parselist(self.app.config["accountsnick"],",")
		self.ap = parselist(self.app.config["accountspass"],",")
		self.disabled = not bool(int(self.app.config["enabled"]))
		i = 0
		for bot in self.an:
			self.botstatus.update([(i,False)])
			i += 1
	def oncommandfromserver(self,command,args,socket):
		try:
			if command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!enable" and args[0] in self.app.admins:
				self.disabled = False
				socket.send("MYSTATUS %i\n" % int(int(self.listfull)+int(self.disabled)*2))
				socket.send("SAYPRIVATE %s %s\n" % (args[0],"Hosting new games enabled"))
				self.app.config["enabled"] = "1"
				self.app.SaveConfig()
			elif command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!disable" and args[0] in self.app.admins:
				self.disabled = True
				socket.send("MYSTATUS %i\n" % int(int(self.listfull)+int(self.disabled)*2))
				socket.send("SAYPRIVATE %s %s\n" % (args[0],"Hosting new games disabled"))
				self.app.config["enabled"] = "0"
				self.app.SaveConfig()
			elif command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!listbans" and args[0] in self.app.admins:
				x = 0
				l0 = []
				for b in self.bans:
					l0.append(b)
					x += 1
					if x >= 5:
						socket.send("SAYPRIVATE %s %s\n" % (args[0],' | '.join(l0)))
						x = 0
						l0 = []
				socket.send("SAYPRIVATE %s %s\n" % (args[0],' | '.join(l0)))
			elif command == "SAIDPRIVATE" and len(args) >= 3 and args[1] == "!ban" and args[0] in self.app.admins:
				toban = args[2:]
				for b in toban:
					if not b in self.bans:
						self.bans.append(b)
						socket.send("SAYPRIVATE %s %s\n" % (args[0],b+" Banned"))
					else:
						socket.send("SAYPRIVATE %s %s\n" % (args[0],b+" is already banned"))
				self.config["bans"] = ','.join(self.bans)
				writeconfigfile("Manager.conf",self.config)
				socket.send("SAYPRIVATE %s %s\n" % (args[0],"Done."))
			elif command == "SAIDPRIVATE" and len(args) >= 3 and args[1] == "!unban" and args[0] in self.app.admins:
				toban = args[2:]
				for b in toban:
					if not b in self.bans:
						socket.send("SAYPRIVATE %s %s\n" % (args[0],b+"is not currently banned"))
					else:
						self.bans.remove(b)
						socket.send("SAYPRIVATE %s %s\n" % (args[0],b+" has been unbanned"))
				self.config["bans"] = ','.join(self.bans)
				writeconfigfile("Manager.conf",self.config)
				socket.send("SAYPRIVATE %s %s\n" % (args[0],"Done."))
			elif command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!spawn" and args[0] not in self.ul and not self.disabled:
				if args[0] in self.bans:
					socket.send("SAYPRIVATE %s %s\n" %(args[0],"\001 Error: You are banned!"))
					return
				freeslot = False
				slot = 0
				for b in self.botstatus:
					if not self.botstatus[b]:
						freeslot = True
						slot = b
						break
				if freeslot:
					self.threads.append(thread.start_new_thread(self.botthread,(slot,self.an[slot],socket,args[0],self.ap[slot],self)))
					socket.send("SAYPRIVATE %s %s\n" %(args[0],self.an[slot]))
					self.ul.append(args[0])
					self.botstatus[slot] = True
					if b + 1 == len(self.botstatus): # The bot spawned was the last one
						self.listfull = True
						socket.send("MYSTATUS 1\n")
				else:
					socket.send("SAYPRIVATE %s %s\n" %(args[0],"\001 Error: All bots are spawned"))

			#elif command == "SAIDPRIVATE" and len(args) == 2 and args[1] == "!spawn" and len(self.ul) >= len(self.an):
			#	socket.send("SAYPRIVATE %s %s\n" %(args[0],"\001 Error: All bots are spawned"))
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
	def updatestatus(self,socket):
		socket.send("MYSTATUS %i\n" % int(int(self.listfull)+int(self.disabled)*2))	
	def onloggedin(self,socket):
		self.updatestatus(socket)	
