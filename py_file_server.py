#!/usr/bin/python
# -*- coding: utf-8 -*-

import SocketServer
import time
import sys
import os
import os.path
import ConfigParser

myHost = ""
verzeichnis = os.path.expanduser("~") 

def now():
	return time.ctime(time.time())
	
class MyClientHandler(SocketServer.BaseRequestHandler):
	def setup(self):
		self.data = None
		self.blksize = 1024
		self.verzeichnis = verzeichnis
		self.gesendet = 0
		print "Client connect:", self.client_address, now()
		
	def handle(self):
		global verzeichnis
		while True:
			self.data = self.request.recv(1024).strip()
			print "Got:", self.data
			if not self.data:
				break
			if self.data == "stop":
				self.shutdown()
			elif self.data.startswith("get"):
				dateiname = self.verzeichnis + os.sep +self.data[4:].strip()
				if os.path.isfile(dateiname):
					f = file(dateiname, "rb")
					while True:
						self.blk = f.read(1024)
						if not self.blk:
							break
						self.send_data(self.blk)
					print "Sent:", self.gesendet
					f.close()
				else:
					self.blk = "Error: not a file or does not exist"
					self.send_data(self.blk)
					print "Sent:", self.gesendet, self.blk
				break
			elif self.data.startswith("ls"):
				try:
					dateiliste = os.listdir(self.verzeichnis)
				except:
					self.blk = "Error: directory does not exist"
					self.send_data(self.blk)
					print "Sent:", self.gesendet, self.blk
					break
				dateiliste.sort()
				if self.data <> "ls -a":
					dateiliste_neu = []
					for i in dateiliste:
						if not i.startswith("."):
							dateiliste_neu.append(i)
					dateiliste = dateiliste_neu[:]
				dateiliste_neu = []
				for i in dateiliste:
					eintrag = i
					if os.path.isdir(os.path.join(self.verzeichnis, i)):
						eintrag = "D," + eintrag + ",0" 
					else:
						eintrag = "F," + eintrag + "," + str(os.path.getsize(os.path.join(self.verzeichnis, i)))
					dateiliste_neu.append(eintrag)
				dateiliste_char = "\n".join(dateiliste_neu)
				send = 0
				i = 0
				while True:
					self.blk = dateiliste_char[send : (i * self.blksize) + self.blksize]
					self.send_data(self.blk)
					send += self.blksize
					if send > len(dateiliste_char):
						break
					i += 1
				print "Sent:", self.gesendet
				break
			elif self.data.startswith("cd"):
				verzeichnis_neu = self.data[3:].strip()
				if verzeichnis_neu == "..":
					self.verzeichnis = os.path.split(self.verzeichnis)[0]
				else:
					if verzeichnis_neu.startswith(os.sep):
						self.verzeichnis = verzeichnis_neu
					else:
						if self.verzeichnis == os.sep:
							self.verzeichnis = self.verzeichnis + verzeichnis_neu
						else:
							self.verzeichnis = self.verzeichnis + os.sep + verzeichnis_neu
				if not os.path.exists(self.verzeichnis) or not os.access(self.verzeichnis, os.R_OK) or not os.path.isdir(self.verzeichnis):
					self.blk = "Error: " + self.verzeichnis + ": That's not a directory or no access"
					self.send_data(self.blk)
					print "Sent:", self.gesendet, self.blk
				else:
					verzeichnis = self.verzeichnis
					self.blk = self.verzeichnis
					self.send_data(self.blk)
					print "Sent:", self.gesendet, self.blk
				break
			elif self.data == "pwd":
				self.blk = self.verzeichnis
				self.send_data(self.blk)
				print "Sent:", self.gesendet, self.blk
				break
		
	def send_data(self, blk):
		try:
			self.request.sendall(blk)
			self.gesendet += len(blk)
		except:
			pass
		
	def shutdown(self):
		server.shutdown()
		print "Server stopped"
	
path = os.path.expanduser("~")
config_path = path + os.sep + ".py_file_server"
config_file = config_path + os.sep + "config"
config = ConfigParser.RawConfigParser()
port_neu = 0
if len(sys.argv) > 1:
	try:
		port_neu = int(sys.argv[1])
	except:
		print "Port seems not to be an integer"
		sys.exit()
while True:
	try:
		x = config.read(config_file)
		myPort = config.getint("Section", "port")
		break
	except:
		config.add_section("Section")
		config.set("Section", "port", "50007")
		if not os.path.exists(config_path):
			os.mkdir(config_path)
		with open(config_file, "wb") as configfile:
			config.write(configfile)
if port_neu > 0 and myPort <> port_neu:
	config.set("Section", "port", port_neu)
	try:
		if not os.path.exists(config_path):
			os.mkdir(config_path)
		with open(config_file, "wb") as configfile:
			config.write(configfile)
		myPort = port_neu
	except:
		sys.exit()
	
myaddr = (myHost, myPort)
SocketServer.ThreadingTCPServer.allow_reuse_address = True
server = SocketServer.ThreadingTCPServer(myaddr, MyClientHandler)
print "Server started and waiting for commands on port " + str(myPort)
server.serve_forever()
