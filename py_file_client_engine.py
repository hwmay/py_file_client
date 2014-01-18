#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import socket
import os.path

class FileClient():
	def __init__(self, host=None, port=None, verzeichnis=None, datei=None):
		if not host:
			self.serverHost = "192.168.1.100"
		else:
			self.serverHost = host
		if not port:
			self.serverPort = 50007
		else:
			self.serverPort = port
		if not verzeichnis:
			self.verzeichnis = os.path.expanduser("~") 
		else:
			self.verzeichnis = verzeichnis
		self.datei = datei
		self.blksize = 1024
		self.sockobj = None
		self.ausgabe = ""
		self.erlaubte_befehle = ("get", "pwd", "ls", "stop", "exit", "cd", "ls -a", "help", "?")
		self.hilfe = ("Datei hierher kopieren, Syntax: get <Dateiname>", "zeige das aktuelle Verzeichnis auf dem Server", "zeige die Dateien im aktuellen Verzeichnis auf dem Server", "Server stoppen", "dieses Programm (den Client) beenden, vorher sollte immer stop des Servers durchgeführt werden", "Verzeichnis im Server wechseln. Syntax: cd <Verzeichnis>, möglich ist auch cd .. (eine Verzeichnisebene höher). Es kann ein absolutes Verzeichnis oder ein relatives im aktuellen Serververzeichnis angegeben werden.", "zeige alle Dateien im aktuellen Verzeichnis auf dem Server, auch die versteckten", "Hilfe anzeigen", "Hilfe anzeigen")
			
	def get_data(self, befehl):
		try:
			self.create_sockobj()
		except:
			if __name__ == "__main__":
				print "Maybe server is not running?"
			return
		self.contact_server(befehl)
		self.sockobj.close()
		
	def create_sockobj(self):
		self.sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sockobj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sockobj.connect((self.serverHost, self.serverPort))
		
	def contact_server(self, line):
		length = 0
		self.sockobj.send(line.encode("utf-8"))
		if line.startswith(self.erlaubte_befehle[0]): # get
			dateiname = line[4:].strip()
			if dateiname:
				if __name__ == "__main__":
					print "Getting", dateiname
					dateiname_komplett = self.verzeichnis + os.sep + os.path.basename(dateiname)
				else:
					dateiname_komplett = self.verzeichnis + os.sep + self.datei
				bytes = 0
				datei_anlegen = True
				while True:
					data = self.sockobj.recv(self.blksize)
					if data.startswith("Error:"):
						self.ausgabe = data
						break
					bytes += len(data)
					if not data:
						if __name__ == "__main__":
							print "Complete"
						f.close()
						self.ausgabe = str(bytes) + " bytes"
						break
					if datei_anlegen:
						datei_anlegen = False
						if os.path.exists(dateiname_komplett):
							self.ausgabe = "Error: filename already exists"
							break
						f = file(dateiname_komplett, "wb")
					f.write(data)
			else:
				print "Please enter a file name after get"
		elif line == self.erlaubte_befehle[1]: # pwd
			while True:
				data = self.sockobj.recv(self.blksize)
				if not data:
					break
				if __name__ == "__main__":
					print line, data
				self.ausgabe = data
		elif line == self.erlaubte_befehle[2] or line == self.erlaubte_befehle[6]: # ls bzw. ls -a
			self.ausgabe = ""
			while True:
				data = self.sockobj.recv(self.blksize)
				self.ausgabe += data
				if not data:
					break
			if __name__ == "__main__":
				print self.ausgabe
		elif line == self.erlaubte_befehle[3]: # stop
			pass
		elif line.startswith(self.erlaubte_befehle[5]) : # cd
			self.ausgabe = ""
			while True:
				data = self.sockobj.recv(self.blksize)
				self.ausgabe += data
				if not data:
					break
			if __name__ == "__main__":
				print self.ausgabe
			
	def work(self, befehl=None):
		while True:
			if __name__ == "__main__":
				aufforderung = "Bitte einen Befehl eingeben (" +", ".join(self.erlaubte_befehle) +"): "
				befehl = raw_input(aufforderung)
			if befehl.startswith(self.erlaubte_befehle[0]):		# get
				self.get_data(befehl)
			elif (befehl == self.erlaubte_befehle[1] 		# pwd
				or befehl == self.erlaubte_befehle[2] 		# ls
				or befehl == self.erlaubte_befehle[6]): 	# ls -a
				self.get_data(befehl)
			elif befehl == self.erlaubte_befehle[3]: 		# stop
				self.get_data(befehl)
				if __name__ == "__main__":
					print "Server stopped"
			elif befehl == self.erlaubte_befehle[4]: 		# exit
				print "Client beendet"
				sys.exit()
			elif befehl.startswith(self.erlaubte_befehle[5]):	# cd
				self.get_data(befehl)
			elif (befehl == self.erlaubte_befehle[7] 		# help
				or befehl == self.erlaubte_befehle[8]):		# ?
				print "\n", "Folgende Befehle können eingegeben und an den Server versendet werden:"
				for i, wert in enumerate(self.erlaubte_befehle):
					print "\n", wert, "-", self.hilfe[i]
			else:
				print "Befehl ungültig, erlaubte Befehle:"
				for i in self.erlaubte_befehle:
					print i
			if __name__ <> "__main__":
				if self.ausgabe <> "":
					return self.ausgabe
				break

if __name__ == "__main__":
	programm = FileClient()
	programm.work()
