#!/bin/env python

import urllib2 
import hashlib 
import json 
import time 
import os 
import pygame 
import threading 
import sys 
import pickle 
taskFile = ".dippycaltasks" 
tokenFile = ".dippycaltoken"

class Task:
	def __init__(self, id, title, completed, folder, context, location, dueDate, dueDateMode, dueTime):
		self.id = id
		self.title = title
		self.completed = completed
		self.folder = folder
		self.context = context
		self.location = location
		self.dueDate = dueDate
		self.dueDateMode = dueDateMode
		self.dueTime = dueTime

# Integrates with Toodledo to manage to do lists
class main:
	def __init__(self, width, height, fonts):
		# Set up some global variables
		self.appid = "DippyCal"
		self.apptoken = "api53c4c13394d94"
		self.email = "czhanacek@gmail.com"
		self.password = "840454"
		self.userid = "td52de0ebb6b773"
		self.width = width
		self.height = height
		self.fonts = fonts           
		self.bgColor = (96, 247, 255)
		self.borderThickness = 10
		self.pageNumber = 1
		self.highlighted = 0
		# Get the old session token and load it as a variable
		try:
			f = open(tokenFile, "r+")
			seshTokenAndEpoch = f.readline()
			self.currentSessionToken, self.sessionTokenCreationTime = seshTokenAndEpoch.split("!")
			f.close()
			#print "Retrieved old session token from file"
		except:
			#print "Couldn't find session token file, requesting new one from server..."
			self.getNewSessionToken()
		
	
	def readTaskFile(self):
		try:
			f = open(taskFile, "r")
		except:
			f = open(taskFile, "w")
			f.close()
			self.readTaskFile(self)
		JSON = f.readline()
		print JSON
		return JSON
	
	def saveTasks(self, JSON):
		try:
			os.remove(taskFile)
		except:
			pass
		f = open(taskFile, "w")
		f.write(JSON)
	def saveToken(self, token, time):
		try:
			os.remove(tokenFile)
		except:
			#print "Couldn't remove .dippycaltoken, maybe it didn't exist"
			pass
		f = open(tokenFile, "w")
		f.write(str(token + "!" + str(time)))
		f.close()
	# Time needs to be "YYYY-MM-DD HH:MM:SS", using a 24 hour clock
	def convertTimeToUNIX(self, timeString):
		pattern = "%Y-%m-%d %H:%M:%S"
		epoch = int(time.mktime(time.strptime(timeString, pattern))) - time.timezone
		return epoch
	
	def convertEpochToTime(self, Epoch):
		pattern = "%Y-%m-%d %H:%M:%S"
		timeString = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(Epoch))
		return timeString
	 # Create hashes for URL requests
	def makeHash(self, values):
		m = hashlib.md5()
		for item in values:
			m.update(item)
		hash = m.hexdigest()
		return hash
	# Lookup the user to get their userid code
	def userLookup(self):
		hash = self.makeHash([self.email, self.appid])
		# Submit the request (using HTTPS)
		url = str("https://api.toodledo.com/2/account/lookup.php?appid=" + self.appid + "&sig=" + hash + "&email=" + self.email + "&pass=" + self.password)
		return self.sendRequest(url)
	# Send a URL request and return the result
	def sendRequest(self, url):
		request = urllib2.urlopen(url)
		result = request.read()
		return result
	# Get a new session token, since they expire after 4 hours
	def getNewSessionToken(self):
		hash = self.makeHash([self.userid, self.apptoken])
		url = str("https://api.toodledo.com/2/account/token.php?userid=" + self.userid + "&appid=" + self.appid + "&sig=" + hash)
		seshToken = self.sendRequest(url)
		decoded = json.loads(seshToken)
		self.currentSessionToken = decoded["token"]
		#print self.currentSessionToken
		self.saveToken(self.currentSessionToken, int(time.time()))
		self.sessionTokenCreationTime = int(time.time())
	def getAccountInfo(self):
		hashedPass = self.makeHash([self.password])
		key = self.makeHash([hashedPass, self.apptoken, self.currentSessionToken])
		url = str("https://api.toodledo.com/2/account/get.php?key=" + key)
		JSON = self.sendRequest(url)
		decoded = json.loads(JSON)
		return decoded
	
	# Get a JSON object of current tasks
	def getTasks(self):
		hashedPass = self.makeHash([self.password])
		key = self.makeHash([hashedPass, self.apptoken, self.currentSessionToken])
		# Get folder, star, priority, context, location, due date, due date mode, and due time for each task
		url = str("https://api.toodledo.com/2/tasks/get.php?key=" + key + "&fields=folder,star,priority,context,location,duedate,duedatemod,duetime")
		#print url
		self.saveTasks(self.sendRequest(url))
	def decodeJSONTasks(self, JSON):
		decoded = json.loads(JSON)
		summary = decoded[0]
		del(decoded[0])
		try:
			numTasks = summary["num"]
			#print decoded print summary
	#                       print "Number of tasks: " + str(numTasks)
			self.unpaginatedTasks = []
			for task in decoded:
				tempTask = Task(task["id"], task["title"], task["completed"], task["folder"], task["context"], task["location"],
						task["duedate"], task["duedatemod"], task["duetime"])
				self.unpaginatedTasks.append(tempTask)
	
		except:
			try:
				if int(summary["errorCode"]) > 1:
					print "Server returned an error"
			except:
				print "Unexpected error occurred"
		
	
	def blankZone(self):
		infill = pygame.Surface((self.width, self.height))
		infill.fill(self.bgColor)
		self.area.blit(infill, ((0, 0), (self.width, self.height)))
	
	def paginateTasks(self):
		lastTaskOnPage = []
		# For pagination of tasks
		theoNextTaskHeight = 0
		currentTask = 0
		paginationFlag = 0
		for task in self.unpaginatedTasks:
			currentTask = currentTask + 1
			titleHeight = self.fonts[1].size(task.title)[1]
			dueDateHeight = self.fonts[3].size(str(task.dueDate))[1]
			theoNextTaskHeight = theoNextTaskHeight + titleHeight + dueDateHeight + 16
			# Add 1 between the title and due date and 15 between tasks
	
			# Check if the nextTask Height is off the page
			if theoNextTaskHeight > (self.height - 25):
				lastTaskOnPage.append(currentTask)
				theoNextTaskHeight = 0
				paginationFlag = 1
		self.paginatedTasks = []
		if paginationFlag == 1:
			for i in lastTaskOnPage:
				taskList = self.unpaginatedTasks[:(i - 1)]
				del self.unpaginatedTasks[:(i - 1)]
				self.paginatedTasks.append(taskList)
			# Don't forget the last few tasks!
			self.paginatedTasks.append(self.unpaginatedTasks)
		else:
			self.paginatedTasks.append(self.unpaginatedTasks)
	def doBorder(self):
		print "Did border"
		self.borderArea = pygame.Surface((self.width, self.height))
		self.borderArea.blit(self.area, (0, 0))
		self.borderColor = (0,0,0)
		if self.highlighted == 1:
			self.borderColor = (255, 0, 0)
		elif self.highlighted == 0:
			self.borderColor = (0,0,0)
		pygame.draw.rect(self.borderArea, self.borderColor, ((0, 0), (self.width, self.height)), self.borderThickness)
		print "Highlighted: " + str(self.highlighted)
		return self.borderArea
	
	# Keep working on the border not erasing past borders 10:30 PM, 11/18/14 - "Good night"
	
	def getConfigs(self):
		self.configOptions = []
		try:
			self.configOptions = pickle.load(open("todo.save", "rb"))
		except:
			pass
	def highlight(self, yesOrNo):
		area = pygame.Surface((self.width, self.height))
		
		return area
	
	def renderTasks(self):
		if (int(time.time()) - int(self.sessionTokenCreationTime)) > 14400:
			#print "Session token outdated, requesting a new one..."
			self.getNewSessionToken()
		else:
			print "We have a current session token"
	
		try:
			self.decodeJSONTasks(self.readTaskFile)
		except:
			#print "No tasks in file, attempting to retrieve some"
			self.getTasks()
			self.decodeJSONTasks(self.readTaskFile())
		self.area = pygame.Surface((self.width, self.height))
		self.borderThickness = 10
		self.paginateTasks()
		self.blankZone()
		self.area.blit(self.doBorder(), (0, 0))
		#self.blankZone()
		# topLeft is actually the left-top of the border of the box
		# We pad in the contents of the box for a nicer visual effect. That's what the "+ 4" a0is
		topLeft = (0 + (self.borderThickness), 0 + (self.borderThickness))
		nextTaskHeight = 0
		todoList = "To Do List"
		titleWidth, titleHeight = self.fonts[1].size(todoList)
		nextTaskHeight = topLeft[1] + titleHeight
		maxWidth = self.width - (1 * self.borderThickness)
		maxHeight = self.height - (1 * self.borderThickness)
		

	# For future word wrap functionality
	#highestTaskWidth = 0


	#if pageNumber > 1:
#                        if len(taskLists) > (pageNumber - 1):
#                                pageNumber = 1
#                        else:
#                                pageNumber = 1
#
#                else:
#                        pageNumber = 1
		for task in self.paginatedTasks[self.pageNumber - 1]:
			# Render the title of the task as titleSurface
			titleSurface = self.fonts[2].render(task.title, True, (0, 0, 0))
	
			if task.dueDate > 0:
				dueDate = "Due: " + str(time.strftime("%m/%d/%Y", time.localtime(task.dueDate)))
			else:
				dueDate = "No due date set"
			# Render the subtitle of the task as subTitleSurface
			subTitleSurface = self.fonts[3].render(dueDate, True, (0, 0, 0))
			if task.completed > 0:
				filledSquare = pygame.draw.rect(self.area, (0, 0, 0), ((7, (nextTaskHeight + 3)), (20, 20)), 0)
			elif task.completed == 0:
				emptySquare = pygame.draw.rect(self.area, (255, 255, 255), ((7, (nextTaskHeight + 3)), (20, 20)), 0)
				filledSquare = pygame.draw.rect(self.area, (0, 0, 0), ((7, (nextTaskHeight + 3)), (20, 20)), 2)
			#print len(titleSurfaces)
			titleSurfaceHeight = titleSurface.get_height()
			titleSurfaceWidth = titleSurface.get_width()
	
			# This functionality is for a future word-wrap capability
	#                        if titleSurfaceWidth > highestTaskWidth:
	#                                highestTaskWidth = titleSurfaceWidth
	
			titleSurfaceLeftTop = (30, (nextTaskHeight))
			subTitleSurfaceSize = subTitleSurface.get_size()
			subTitleSurfaceLeftTop = (titleSurfaceLeftTop[0], titleSurfaceLeftTop[1] + titleSurfaceHeight + 1)
	
	
	
			nextTaskHeight = nextTaskHeight + subTitleSurfaceSize[1] + titleSurfaceHeight + 15
			self.area.blit(titleSurface, titleSurfaceLeftTop)
			self.area.blit(subTitleSurface, subTitleSurfaceLeftTop)
			#pygame.display.flip()
		titleWidth, titleHeight = self.fonts[1].size(todoList)
		title = self.fonts[1].render(todoList, True, (0, 0, 0))
		titleLeftTop = (topLeft[0], topLeft[1])
		self.area.blit(title, titleLeftTop)
		nextTaskHeight = topLeft[1] + titleHeight
		return self.area



	
	def doArea(self):
		# Establish variables Eventually these will come from a config file
		area = self.renderTasks()
		return area


