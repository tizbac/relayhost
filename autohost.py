from colors import *
from ParseConfig import *
import commands
import thread
import signal
import os
import time
import udpinterface
import subprocess
import traceback
import sys
from utilities import *
def pm(s,p,m):
	print yellow+"PM To:%s, Message: %s" %(p,m) + normal
	s.send("SAYPRIVATE %s %s\n" %(p,m))
def logc(s,m):
	s.send("SAY autohost %s\n" % m)
def loge(s,m):
	s.send("SAYEX autohost %s\n" % m)
class Main:
	sock = 0
	hosted = 0
	battleowner = ""
	battleid = 0
	status = 0
	pr = 0
	noowner = True
	script = ""
	ingame = 0
	used = 0
	app = 0
	hosttime = 0.0
	gamestarted = 0
	users = dict()
	def ecb(self,event,data):
		try:
			if getbot(self.users[self.battleowner]) == 1:
				ags = []
				data2 = ""
				for c in data:
					if ord(c) < 17:
						ags.append(ord(c))
					else:
						data2 += c
				
				pm(self.sock,self.battleowner,"#"+str(event)+"#".join(ags)+" "+data2)
		except:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			loge(socket,"*** EXCEPTION: BEGIN")
			for line in exc:
				loge(self.sock,line)
			loge(socket,"*** EXCEPTION: END")
	def gs(self):# Game started
		self.gamestarted = 1
	def onloggedin(self,socket):
		self.hosted = 0
		self.users = dict()
		self.sock = socket
	def mscb(self,p,msg):
		try:
			if p == self.battleowner:
				if msg.startswith("!"):
					if msg.startswith("!kick") and msg.count(self.app.config["nick"]) > 0:
						self.u.sayingame("I'm not stupid like chanserv that mutes itself")
						return
					if msg.startswith("!exit"):
						self.u.sayingame("You cannot ragequit!")
						return
					g = msg.replace("!","/")
					self.u.sayingame(g)
		except:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			loge(socket,"*** EXCEPTION: BEGIN")
			for line in exc:
				loge(self.sock,line)
			loge(socket,"*** EXCEPTION: END")
		
	def timeoutthread(self):
		while 1:
			time.sleep(20.0)
			try:
				if not self.hosted == 1 and not self.ingame == 1:
					print "Timeouted hosting"
					os.kill(os.getpid(),signal.SIGKILL)
			except:
				pass
			
	def startspring(self,socket,g):
		try:
			self.gamestarted = 0
			self.u.reset()
			if self.ingame == 1:
				socket.send("SAYBATTLEEX *** Error: game is already running\n")
				return
			self.ingame = 1
			socket.send("SAYBATTLEEX *** Starting game...\n")
			socket.send("MYSTATUS 1\n")
			st = time.time()
			#status,j = commands.getstatusoutput("spring-dedicated "+os.path.join(os.environ['HOME'],"%f.txt" % g ))
		
			self.pr = subprocess.Popen((self.app.config["springdedpath"],os.path.join(os.environ['HOME'],"%f.txt" % g )))
			status = self.pr.wait()
		
			et = time.time()
		
			"""lns = j.split("\n")
			if status != 0 or lns[len(lns)-2].startswith("Exception raised:") or et - st < 2.0:
				socket.send("SAYBATTLEEX *** Error: Spring Exited with status %i\n" % status)
				g = j.split("\n")
				for h in g:
					socket.send("SAYBATTLEEX *** "+h+"\n")"""
			socket.send("MYSTATUS 0\n")
			socket.send("SAYBATTLEEX *** Game ended\n")
		except:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			loge(socket,"*** EXCEPTION: BEGIN")
			for line in exc:
				loge(socket,line)
			loge(socket,"*** EXCEPTION: END")
		try:
			if int(self.config["keepscript"]) == 0:
				os.remove(os.path.join(os.environ['HOME'],"%f.txt" % g))
		except:
			pass
		self.ingame = 0
		self.gamestarted = 0
		if self.noowner == True:
			print "Exiting"
			os.kill(os.getpid(),signal.SIGKILL)
	def onload(self,tasc):
		try:
			self.app = tasc.main
			self.config = readconfigfile("Autohost.cfg")
			self.hosttime = time.time()
			thread.start_new_thread(self.timeoutthread,())
			self.u = udpinterface.UDPint(int(self.app.config["ahport"]),self.mscb,self.gs,self.ecb)
		except:
			exc = traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
			
			
			for line in exc:
				print line
			
	def oncommandfromserver(self,command,args,s):
		#print "From server: %s | Args : %s" % (command,str(args))
		self.sock = s
		if command == "ADDUSER" and len(args) > 0:
			self.users.update([(args[0],0)])
		if command == "CLIENTSTATUS" and len(args) > 1:
			self.users.update([(args[0],int(args[1]))])
		if command == "SAIDPRIVATE" and args[0] not in self.config["bannedusers"] and args[0] == self.app.config["spawnedby"]:
			if args[1] == "!openbattle" and not self.hosted == 1:
				if len(args) < 6:
					print "Got invalid openbattle with params:"+" ".join(args)
					return
				args[5] = self.app.config["hostport"]
				print "OPENBATTLE "+" ".join(args[2:])
				s.send("OPENBATTLE "+" ".join(args[2:])+"\n")
				self.battleowner = args[0]
				self.noowner = False
				return
			elif args[1] == "!openbattle" and self.hosted == 1:
				pm(s,args[0],"E1 | Battle is already hosted")
				return
			if self.hosted == 1 and not self.gamestarted == 1:
				if args[1] == "!addstartrect" and self.hosted == 1:
					s.send("ADDSTARTRECT "+" ".join(args[2:])+"\n")
				if args[1] == "!setscripttags" and self.hosted == 1:
					s.send("SETSCRIPTTAGS "+" ".join(args[2:])+"\n")
				if args[1] == "!removestartrect" and self.hosted == 1:
					s.send("REMOVESTARTRECT "+" ".join(args[2:])+"\n")
				if args[1] == "!leavebattle" and args[0] == self.battleowner:
					s.send("LEAVEBATTLE\n")
					self.hosted = 0
				if args[1] == "!updatebattleinfo" and args[0] == self.battleowner:
					s.send("UPDATEBATTLEINFO "+" ".join(args[2:])+"\n")
				if args[1] == "!kickfrombattle" and args[0] == self.battleowner:
					s.send("KICKFROMBATTLE "+" ".join(args[2:])+"\n")
				if args[1] == "!addbot" and args[0] == self.battleowner:
					s.send("ADDBOT "+" ".join(args[2:])+"\n")
				if args[1] == "!handicap" and args[0] == self.battleowner:
					s.send("HANDICAP "+" ".join(args[2:])+"\n")
				if args[1] == "!forceteamcolor" and args[0] == self.battleowner:
					s.send("FORCETEAMCOLOR "+" ".join(args[2:])+"\n")
				if args[1] == "!forceallyno" and args[0] == self.battleowner:
					s.send("FORCEALLYNO "+" ".join(args[2:])+"\n")
				if args[1] == "!forceteamno" and args[0] == self.battleowner:
					s.send("FROCETEAMNO "+" ".join(args[2:])+"\n")
				if args[1] == "!disableunits" and args[0] == self.battleowner:
					s.send("DISABLEUNITS "+" ".join(args[2:])+"\n")
				if args[1] == "!enableallunits" and args[0] == self.battleowner:
					s.send("ENABLEALLUNITS "+" ".join(args[2:])+"\n")
				if args[1] == "!removebot" and args[0] == self.battleowner:
					s.send("REMOVEBOT "+" ".join(args[2:])+"\n")
				if args[1] == "!updatebot" and args[0] == self.battleowner:
					s.send("UPDATEBOT "+" ".join(args[2:])+"\n")
				if args[1] == "!forcespectatormode" and args[0] == self.battleowner:
					s.send("FORCESPECTATORMODE "+" ".join(args[2:])+"\n")
				if args[1] == "!cleanscript" and args[0] == self.battleowner:
					self.script = ""
				if args[1] == "!appendscriptline" and args[0] == self.battleowner:
					if not len(self.script) > 200000:
						self.script += " ".join(args[2:])+"\n"
				if args[1] == "!startgame" and args[0] == self.battleowner:
					s.send("MYSTATUS 1\n")
					g = time.time()
					try:
						os.remove(os.path.join(os.environ['HOME'],"%f.txt" % g))
					except:
						pass
					f = open(os.path.join(os.environ['HOME'],"%f.txt" % g),"aw")
					s1 = self.script.find("MyPlayerNum=")
					s2 = self.script[s1:].find(";")+1+s1
					print s1
					print s2
					if s1 < 0:
						#loge(s,"*** WARNING : MyPlayerNum not found!")
						s1 = 0
						s2 = len(self.script)-1
					else:					
						self.script = self.script.replace(self.script[s1:s2],"MyPlayerNum=0;")
					s1 = self.script.find("MyPlayerName=")
					s2 = self.script[s1:].find(";")+1+s1
					print s1
					print s2
					self.script = self.script.replace(self.script[s1:s2],"MyPlayerName=%s;\nAutoHostPort=%i;" % (self.app.config["nick"],int(self.app.config["ahport"])))
					f.write(self.script)
					f.close()
					
					thread.start_new_thread(self.startspring,(s,g))
			else:
				pm(s,args[0],"E2 | Battle is not hosted")
			
		if command == "OPENBATTLE":
			self.hosted = 1
			self.battleid = int(args[0])
			self.used = 1
		if command == "SERVERMSG":
			pm(s,self.battleowner," ".join(args))
		if command == "LEFTBATTLE" and int(args[0]) == self.battleid and args[1] == self.battleowner:
			if  not self.gamestarted == 1:
				print "Exiting"
				s.send("LEAVEBATTLE\n")
				try:
					os.kill(self.pr.pid,signal.SIGKILL)
				except:
					pass
				os.kill(os.getpid(),signal.SIGKILL)
				
			self.noowner = True

		if command == "REMOVEUSER" and args[0] == self.battleowner:
			if  not self.gamestarted == 1:
				print "Exiting"
				try:
					os.kill(self.pr.pid,signal.SIGKILL)
				except:
					pass
				os.kill(os.getpid(),signal.SIGKILL)
			self.noowner = True
	def onloggedin(self,socket):
		self.noowner = True
		self.hosted = 0	
		if self.ingame == 1:
			socket.send("MYSTATUS 1\n")
