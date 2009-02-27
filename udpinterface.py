import socket
import thread
import string
import traceback,sys
class UDPint:
	def __init__(self,port,messagecb,startedcb,eventcb):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind(("localhost",int(port)))
		self.players = dict()
		self.addr = ""
		thread.start_new_thread(self.mainloop,(messagecb,startedcb,eventcb))
		print "UDP Listening on port "+str(port)
	def reset(self):
		self.players = dict()
	def mainloop(self,messagecb,scb,eventcb):
		while 1:
			try:
				
				data, address = self.s.recvfrom(8192)
				self.addr = address
				event = ord(data[0])
				print "Received event %i from %s" % (event,str(address))
				if event == 10:
					n = ord(data[1])
					name = data[2:]
					self.players.update([(n,name)])
				if event == 13:
					n = ord(data[1])
					text = data[3:]
					if not text.lower().startswith("a:"):
						messagecb(self.players[n],text)
				if event == 2:
					scb()
				eventcb(ord(data[0]),data[1:])
			except:
				print '-'*60
				traceback.print_exc(file=sys.stdout)
				print '-'*60
	def sayingame(self,text):
		print "Sending %s to spring" % text
		try:
			self.s.sendto(text,self.addr)
		except:
			print '-'*60
			traceback.print_exc(file=sys.stdout)
			print '-'*60
