#!/bin/env python

import urllib2
import hashlib
import json
import time
import os
import pygame
import threading
import importlib
import sys
from pygame.locals import *

#import todoDippyCal as todoListMod
appid = "DippyCal"
apptoken = ""
email = ""
password = ""
userid = ""
taskFile = ".dippycaltasks"
tokenFile = ".dippycaltoken"


class Weather:
	def __init__(self):
		pass
	def sendRequest(url):
		request = urllib2.urlopen(url)
		result = request.read()
		return result
	def getWeather(self):
		# Get folder, star, priority, context, location, due date, due date mode, and due time for each task
		url = str("http://api.openweathermap.org/data/2.5/weather?q=Bainbridge-Island")
		#print url
		self.saveWeatherFile(self.sendRequest(url))
	def saveWeatherFile(self, JSON):
		os.remove(weatherFile)
		f = open(weatherFile, "w")
		f.write(JSON)
	def readWeatherFile(self):
		f = open(weatherFile, "r")
		JSON = f.readline()
		return JSON
	def updateWeather(JSON):
		weather = json.loads(JSON)
		return weather
	
	
def updateScreen(surfaceHeight, surfaceWidth, surfaceLeftTop, surface, screen, bgColor=(255, 255, 255)):
	infill = pygame.Surface((surfaceWidth, surfaceHeight))
	infill.fill(bgColor)
	screen.blit(infill, surfaceLeftTop)
	screen.blit(surface, surfaceLeftTop)
	pygame.display.update(surfaceLeftTop, (surfaceWidth, surfaceHeight))
	
def importExtras():
	directory = os.getcwd()
	files = os.listdir(directory)
	extrasList = []
	print files
	for extra in files:
		if extra != "dippyCal.py" and extra.find(".") != 0:
			extra = extra.split('.')[0]
			module = __import__(extra)
			extrasList.append(module)
	return extrasList

# WRAPPING TEXT IS NOT SUPPORTED YET
#def wrapText(text, maxWidth, font, textSurfaces=[]):
#	width, height = font.size(text)
#        droppedWords = []
#	wrappingFlag = 0
#	if width > maxWidth:
#		wrappingFlag = 1
#		textWords = text.split(" ")
#               droppedWords.append(textWords.pop())
#               width, height = regFont.size(task.title)
#	if wrappingFlag > 0:
#		nextText = ""
#		for i in range(len(droppedWords)):
#			nextText = nextText + droppedWords[-1]
#		finalText = ""
#		# Replace the spaces between words
#		for i in range(len(textWords) - 2):
#			finalText = finalText + textWords[i] + " "
#		finalText = finalText + textWords[len(textWords) - 1]
#
#		textSurface = font.render(finalText, True, (0, 0, 0))
#		textSurfaces.append(textSurface)
#		wrapText(nextText, maxWidth, font, textSurfaces)
#	else:
#		textSurface = font.render(text, True, (0, 0, 0))
#		textSurfaces.append(textSurface)
#		return textSurfaces


def renderWeather(currentConditions, borderTopLeft, screen, titleFont, subFont, regFont, borderMaxWidth=400, borderMaxHeight=400):
	print "Nothing here yet"

def setupScreen():
	screen = pygame.display.set_mode()
	screen.fill((255, 255, 255))
	pygame.mouse.set_visible(0)
	pygame.display.flip()
	screenHeight = screen.get_height()
	screenWidth = screen.get_width()
	return screen, screenHeight, screenWidth
def setupFonts(fontPath=""):
	if(fontPath == ""):
		fontPath = pygame.font.get_default_font();
	titleFont = pygame.font.SysFont(fontPath, 80)
	areaFont = pygame.font.SysFont(fontPath, 50)
	subTitleFont = pygame.font.SysFont(fontPath, 30)
	regFont = pygame.font.SysFont(fontPath, 20)
	return [titleFont, areaFont, subTitleFont, regFont]

class Board:
	def __init__(self, screen, width, height, fonts, backgroundColor):
		self.screen = screen
		self.width = width
		self.height = height
		self.fonts = fonts
		self.backgroundColor = backgroundColor
		self.updateQueue = []
		self.highlightedModule = 0
	def addAreaToQueue(self, surface, leftTop):
		self.screen.blit(surface, leftTop)
		self.updateQueue.append([leftTop, (surface.get_size())])
	def processUpdateQueue(self):
		for region in self.updateQueue:
			pygame.display.update(region[0], region[1])
	def doTitle(self, titleText="DippyCal", titleColor=(0,0,0)):
		title = fonts[0].render(titleText, True, titleColor)
		titleLeftTop = (((self.width / 2) - (title.get_width() / 2)), 0)
		self.screen.blit(title, titleLeftTop)
		self.addAreaToQueue(title, titleLeftTop)


# This class is basically the imported module with some metadata
class Area:
	def __init__(self, board, module, width, height, leftTop, availableFonts):
		self.highlighted = 0
		self.board = board
		self.module = module.main(width, height, availableFonts)
		self.width = width
		self.height = height
		self.leftTop = leftTop
		self.availableFonts = availableFonts
		self.surface = []
	def render(self):
		surface = self.module.doArea()
		self.board.addAreaToQueue(surface, self.leftTop)
		self.surface = surface
	def highlight(self):
		self.highlighted = 1
		self.module.highlighted = 1
		self.borderSurface = self.module.doBorder()
		self.board.addAreaToQueue(self.borderSurface, self.leftTop)
		self.board.highlightedModule = self
	def clearArea(self, width, height, leftTop):
		cleared = pygame.Surface((width, height))
		cleared.fill(self.board.backgroundColor)
		self.board.addAreaToQueue(cleared, leftTop)
	def unhighlight(self):
		self.highlighted = 0
		self.module.highlighted = 0
		self.borderSurface = self.module.doBorder()
		self.board.addAreaToQueue(self.borderSurface, self.leftTop)
		self.board.highlightedModule = 0
	def highlightToggle(self):
		if self.highlighted == 1:
			self.highlighted = 0
			self.unhighlight()
		else:
			self.highlighted = 1
			self.highlight()
	def move(self):
		moving = 1
		while moving:
			board.processUpdateQueue()
			for event in pygame.event.get():
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_q:
						pygame.quit()
						print "\n"
						sys.exit()
					elif event.key == pygame.K_UP:
						self.board.highlightedModule.moveUp()
					elif event.key == pygame.K_DOWN:
						self.board.highlightedModule.moveDown()
					elif event.key == pygame.K_LEFT:
						self.board.highlightedModule.moveLeft()
					elif event.key == pygame.K_RIGHT:
						self.board.highlightedModule.moveRight()
					elif event.key == pygame.K_RETURN:
						pygame.display.flip()
						moving = 0
	
	def moveDown(self):
		oldLeftTop = self.leftTop
		x = self.leftTop[1]
		y = self.leftTop[0]
		x += 5
		self.leftTop = (y, x)
		self.clearArea(self.width, self.height + 5, oldLeftTop)
		self.board.addAreaToQueue(self.surface, self.leftTop)
	def moveLeft(self):
		oldLeftTop = self.leftTop
		x = self.leftTop[1]
		y = self.leftTop[0]
		y -= 5
		self.leftTop = (y, x)
		self.clearArea(self.width + 5, self.height, oldLeftTop)
		self.board.addAreaToQueue(self.surface, self.leftTop)
	def moveRight(self):
		oldLeftTop = self.leftTop
		x = self.leftTop[1]
		y = self.leftTop[0]
		y += 5
		self.leftTop = (y, x)
		self.clearArea(self.width + 5, self.height, oldLeftTop)
		self.board.addAreaToQueue(self.surface, self.leftTop)
	
	def moveUp(self):
		oldLeftTop = self.leftTop
		x = self.leftTop[1]
		y = self.leftTop[0]
		x -= 5
		self.clearArea(self.width, self.height + 5, oldLeftTop)
		self.leftTop = (y, x)
		self.board.addAreaToQueue(self.surface, self.leftTop)

#						sys.exit()

# Start the actual program
pygame.init()
screen, screenHeight, screenWidth = setupScreen()
fonts = setupFonts()
board = Board(screen, screenWidth, screenHeight, fonts, (255, 255, 255))
board.doTitle()
leftTop = (50, 50)
areaWidth = 800
areaHeight = 400
modules = importExtras()
areas = []
for module in modules:
	area = Area(board, module, areaWidth, areaHeight, leftTop, fonts)
	area.render()
	#board.addAreaToQueue(area.surface, area.leftTop)
	areas.append(area)

#accountInfo = todo.getAccountInfo()

#lastTaskEdit = accountInfo["lastedit_task"]


#getTasksLoop = threading.Thread(target=todo.scheduledGetTasks)
#getTasksLoop.start()
# Try to access tasks file
#try:
#	todo.decodeJSONTasks(todo.readTaskFile())
#except:
#print "No tasks in file, attempting to retrieve some"
#	todo.getTasks()

#tasks = todo.decodeJSONTasks(todo.readTaskFile())
#pageNumber = 1
#print paginateTasks(tasks, subTitleFont, regFont, 400)
#tasks = todoListMod.paginateTasks(tasks, subTitleFont, regFont, 400)
#taskBox = (130, 160)
#todoListMod.renderTasks(tasks, pageNumber, taskBox, screen, areaFont, subTitleFont, regFont)
#weather = weather.decodeJSONWeather(weather.readWeatherFile())
while 1:
	board.processUpdateQueue()
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				pygame.quit()
				print "\n"
				sys.exit()
			elif event.key == pygame.K_h:
				areas[0].highlightToggle()
			elif event.key == pygame.K_m:
				board.highlightedModule.move()
			#elif event.key == pygame.K_w:


