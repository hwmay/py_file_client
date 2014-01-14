#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import ConfigParser
from PyQt4 import QtGui, QtCore
from py_file_client_ui import Ui_MainWindow as MainWindow
from py_file_client_engine import FileClient

class MeinDialog(QtGui.QMainWindow, MainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		self.setupUi(self)
		
		# Slots einrichten
		self.connect(self.pushButtonDirClient, QtCore.SIGNAL("clicked()"), self.onDirectory)
		self.connect(self.pushButtonUp, QtCore.SIGNAL("clicked()"), self.onDirectoryUp)
		self.connect(self.pushButtonClear, QtCore.SIGNAL("clicked()"), self.onProtocolClear)
		self.connect(self.pushButtonGet, QtCore.SIGNAL("clicked()"), self.onGetFiles)
		self.connect(self.pushButtonStop, QtCore.SIGNAL("clicked()"), self.onStopServer)
		self.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int, int)"), self.onDown)
		self.connect(self.checkBoxHidden, QtCore.SIGNAL("stateChanged(int)"), self.onHidden)
		
		settings = QtCore.QSettings()
		window_size = settings.value("py_file_client/Size", QtCore.QVariant(QtCore.QSize(600, 500))).toSize()
		self.resize(window_size)
		window_position = settings.value("py_file_client/Position", QtCore.QVariant(QtCore.QPoint(0, 0))).toPoint()
		self.move(window_position)
		
		self.path = os.path.expanduser("~")
		self.config_path = self.path + os.sep + ".py_file_client"
		self.config_file = self.config_path + os.sep + "config"
		self.config = ConfigParser.RawConfigParser()
		while True:
			try:
				x = self.config.read(self.config_file)
				self.host = self.config.get("Section", "host")
				self.port = self.config.getint("Section", "port")
				self.path = self.config.get("Section", "dir")
				break
			except:
				self.config.add_section("Section")
				self.config.set("Section", "host", "192.168.1.100")
				self.config.set("Section", "port", "50007")
				self.config.set("Section", "dir", self.path)
				try:
					if not os.path.exists(self.config_path):
						os.mkdir(self.config_path)
					with open(self.config_file, "wb") as configfile:
						self.config.write(configfile)
				except:
					sys.exit()
		
		self.lineEditDirectoryClient.setText(self.path)
		self.lineEditIP.setText(self.host)
		self.lineEditPort.setText(str(self.port))
		self.blksize = 1024
		self.sockobj = None
		self.threadPool = []
		
		contact_server = FileClient(host = self.host, port = self.port)
		res = contact_server.work("pwd")
		if res:
			self.lineEditDirectory.setText(res)
			contact_server = FileClient(host = self.host, port = self.port)
			res = contact_server.work("ls")
			if res:
				self.filelist = res.split("\n")
				self.output_in_table()
		else:
			self.listWidget.addItem(self.trUtf8("Maybe server is not running?"))
			self.listWidget.scrollToBottom()
		
	def onDirectory(self):
		datei = QtGui.QFileDialog.getExistingDirectory(self, self.trUtf8("Select directory"), self.lineEditDirectoryClient.text())
		if datei:
			self.path = str(datei)
			self.lineEditDirectoryClient.setText(self.path)
		
	def onDirectoryUp(self):
		contact_server = FileClient(host = self.host, port = self.port)
		contact_server.work("cd ..")
		res = contact_server.work("pwd")
		if res:
			self.lineEditDirectory.setText(res)
			if self.checkBoxHidden.checkState():
				res = contact_server.work("ls -a")
			else:
				res = contact_server.work("ls")
			self.filelist = res.split("\n")
			self.output_in_table()
		else:
			self.listWidget.addItem(self.trUtf8("Maybe server is not running?"))
			self.listWidget.scrollToBottom()
		
	def onProtocolClear(self):
		self.listWidget.clear()
		
	def onGetFiles(self):
		# generic thread using signal
		self.threadPool.append(GenericThread(self.getFiles))
		# signal for updating protocol listwidget
		self.disconnect( self, QtCore.SIGNAL("add(QString)"), self.add)
		self.connect( self, QtCore.SIGNAL("add(QString)"), self.add)
		self.threadPool[len(self.threadPool)-1].start()
		
	def getFiles(self):
		app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
		items = self.tableWidget.selectedItems()
		for i in items:
			if i.column() == 1:
				befehl = self.trUtf8("Getting ") + i.text() + " ..."
				self.emit(QtCore.SIGNAL('add(QString)'), befehl)
				contact_server = FileClient(host = self.host, port = self.port, verzeichnis = self.lineEditDirectoryClient.text(), datei = i.text())
				res = contact_server.work("get " + unicode(i.text()))
				if res:
					self.emit(QtCore.SIGNAL('add(QString)'), res)
				self.emit(QtCore.SIGNAL('add(QString)'), "-----------------------------------------------")
		app.restoreOverrideCursor()
		
	def onDown(self, zeile, spalte, directory = None):
		if not directory:
			directory = (QtGui.QTableWidgetItem.text(self.tableWidget.item(zeile, 1)))
		contact_server = FileClient(host = self.host, port = self.port)
		res = contact_server.work("cd " + unicode(directory))
		if res.startswith("Error:"):
			newitem = QtGui.QListWidgetItem(res.decode("utf-8"))
			newitem.setTextColor(QtGui.QColor("red"))
			self.listWidget.addItem(newitem)
			self.listWidget.addItem("-----------------------------------------------")
			self.listWidget.scrollToBottom()
			return
		res = contact_server.work("pwd")
		self.lineEditDirectory.setText(res.decode("utf-8"))
		if self.checkBoxHidden.checkState():
			res = contact_server.work("ls -a")
		else:
			res = contact_server.work("ls")
		if res:
			self.filelist = res.split("\n")
			self.output_in_table()
		else:
			self.tableWidget.clearContents()
			
	def onHidden(self, status):
		if status == 0:
			contact_server = FileClient(host = self.host, port = self.port)
			res = contact_server.work("ls")
			if res:
				self.filelist = res.split("\n")
				self.output_in_table()
		else:
			contact_server = FileClient(host = self.host, port = self.port)
			res = contact_server.work("ls -a")
			if res:
				self.filelist = res.split("\n")
				self.output_in_table()
				
	def onStopServer(self):
		contact_server = FileClient(host = self.host, port = self.port)
		contact_server.work("stop")
		self.listWidget.addItem(self.trUtf8("Server stopped"))
		self.listWidget.scrollToBottom()
		
	def output_in_table(self):
		row = 0
		column = 0
		self.tableWidget.setAlternatingRowColors(True)
		self.tableWidget.clearContents()
		self.tableWidget.setRowCount(len(self.filelist))
		self.tableWidget.setColumnCount(3)
		self.tableWidget.setSortingEnabled(False)
		zeile = []
		for i in self.filelist:
			zeile = i.strip().split(",")
			for j in zeile:
				if column == 0:
					if j == "D":
						newitem = QtGui.QTableWidgetItem()
						newitem.setIcon(QtGui.QIcon("./Icons" + os.sep + "folder.svg"))
					else:
						newitem = QtGui.QTableWidgetItem()
						newitem.setIcon(QtGui.QIcon("./Icons" + os.sep + "file-zoom-in.png"))
				else:
					newitem = QtGui.QTableWidgetItem(j.decode("utf-8"))
				self.tableWidget.setItem(row, column, newitem)
				column += 1
			column = 0
			row += 1
		self.tableWidget.resizeColumnsToContents()
		self.tableWidget.resizeRowsToContents()
		self.tableWidget.setSortingEnabled(True)
		self.tableWidget.sortItems(1)
		self.tableWidget.scrollToTop()
		
	def add(self, text):
		""" Add item to protocol list widget """
		if unicode(text).startswith("Error:"):
			newitem = QtGui.QListWidgetItem(text)
			newitem.setTextColor(QtGui.QColor("red"))
			self.listWidget.addItem(newitem)
		else:
			self.listWidget.addItem(text)
		self.listWidget.scrollToBottom()
		
	def keyPressEvent(self, event):
		if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
			self.onDown(0, 0, directory = self.lineEditDirectory.text())
		
	def closeEvent(self, event):
		settings = QtCore.QSettings()
		settings.setValue("py_file_client/Size", QtCore.QVariant(self.size()))
		settings.setValue("py_file_client/Position", QtCore.QVariant(self.pos()))
		self.config.set("Section", "host", str(self.lineEditIP.text()))
		self.config.set("Section", "port", str(self.lineEditPort.text()))
		self.config.set("Section", "dir", str(self.lineEditDirectoryClient.text()))
		try:
			if not os.path.exists(self.config_path):
				os.mkdir(self.config_path)
			with open(self.config_file, "wb") as configfile:
				self.config.write(configfile)
		except:
			sys.exit()
		
class GenericThread(QtCore.QThread):
	def __init__(self, function, *args, **kwargs):
		QtCore.QThread.__init__(self)
		self.function = function
		self.args = args
		self.kwargs = kwargs

	def __del__(self):
		self.wait()

	def run(self):
		self.function(*self.args, **self.kwargs)
		return
		
app = QtGui.QApplication(sys.argv)
app.setOrganizationName("py_file_client")
app.setOrganizationDomain("py_file_client")
locale = QtCore.QLocale.system().name()
locale = "en_EN"
appTranslator = QtCore.QTranslator()
if appTranslator.load("py_file_client_" + locale, os.getcwd()):
	app.installTranslator(appTranslator)
dialog = MeinDialog()
dialog.show()
sys.exit(app.exec_())