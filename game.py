# Author: Seamus Boots
# Desc.: This file controls the main logic for the game.
# Input: Player controls and clicks the mouse. The escape key can quit the game.
# Output: Graphical elements inside the window move around.
# Attrib.: Chimpanzee by Mike Koenig is licensed under CC 3.0.

import os
import simpleaudio as sa

from random import choice, randint
from types import MethodType
from time import sleep
from gui import GUI, Timer, Button
from sac_graphics import Point, Rectangle, Image, GraphWin, Text

class Game():
	
	def __init__(self, window, homeGUI: GUI, gameGUI: GUI):
		
		self.window = window
		self.homeGUI = homeGUI
		self.gameGUI = gameGUI
		
		self.isPlaying = False
		self.isGameOver = False
		
		self.timer = Timer(Point(100, 100))
		
		playerW = 25
		playerH = 25
		
		# 25x25 Rectangle
		self.playerRect = Rectangle(Point(0, 0), Point(playerW, playerH))
		self.playerRect.halfW = (playerW // 2)
		self.playerRect.halfH = (playerH // 2)
		self.playerRect.hasMouseClick = False
		self.playerRect.hasMouseMove = True
		self.playerRect.hasKeyPress = False
		self.playerRect.setFill("green")
		self.playerRect.mouseMove = MethodType(_playerRectMouseMove, self.playerRect)
		
		self.obsHandler = ObstacleHandler(self.window, self.playerRect)
		
		self.songChoices = os.listdir("audio")
		self.currentSong = choice(self.songChoices)
		self.musicWave = None
		self.musicPlay = None
		
		self.playNextSong()
	
	def gameLoop(self):
		
		key   = self.window.checkKey()
		mouse = self.window.checkMouse()
		
		# Game Loop
		while key != "Escape":
			
			self.window.update()
			
			self.homeGUI.poll(key, mouse)
			self.gameGUI.poll(key, mouse)
			
			# Handles checking for input with a closed window
			try:
				
				key   = self.window.checkKey()
				mouse = self.window.checkMouse()
			
			except Exception as e:
				
				# Safe exit without errors
				self.window.close()
				exit()
			
			# Sleep for 10 milliseconds every game "tick"
			# => 100 ticks in a second => 100 FPS!!!
			sleep(0.01)
			
			# When the current song stops, play the other, only if
			# the game over video isn't playing
			if not self.musicPlay.is_playing() and not self.isGameOver:
				self.playNextSong()
			
			# Main game logic for obstacles and stuff...
			if self.isPlaying:
				
				self.obsHandler.poll(self.timer)
				
				# If the player collided, tell them its Game Over
				if self.obsHandler.hasCollided():
					
					self.gameOver()
				
				isTick100 = self.timer.tick()
				
				if isTick100:
					
					# Decrease the time of the obstacles by a few milliseconds,
					# making the game harder every second...
					reduction = randint(4, 8)
					Obstacle.minT -= reduction
					Obstacle.maxT -= reduction
					
					# Send 3 obstacles every second!!!
					for _ in range(3):
						self.obsHandler.sendNewObs()
	
	def newGame(self):
		
		self.gameGUI.undraw()
		self.gameGUI.delAll()
		
		# Re-add the timer and player rect
		self.gameGUI.addAll(self.timer,
							self.playerRect)
		
		self.gameGUI.draw(self.window)
		
		# Reset obstacle times to their defaults
		Obstacle.minT = Obstacle.DEFAULT_MIN_T
		Obstacle.maxT = Obstacle.DEFAULT_MAX_T
		
		# Set the flags
		self.isGameOver = False
		self.isPlaying = True
	
	def gameOver(self):
		
		self.musicPlay.stop()
		
		# Play a sound effect
		sa.WaveObject.from_wave_file("audio/chimpanzee.wav").play()
		
		self.isGameOver = True
		self.isPlaying = False
		
		self.obsHandler.destroyAll()
		
		finalScore = self.timer.getTime()
		
		highscores = getHighscores()
		
		# Only save the highscore if needed
		if finalScore not in highscores:
			highscores.append(finalScore)
		
		# Sorts the list of scores in descending order,
		# where the highest score is first
		highscores.sort(reverse=True)
		
		# Re comprehend the list to store strings
		highscores = [str(s) + '\n' for s in highscores]

		highscoresFileName = "data/highscores.txt"

		# Clear the files contents
		open(highscoresFileName, "w").close()
		
		with open(highscoresFileName, "w") as highscoresFile:
			
			# Rewrite the files contents
			highscoresFile.writelines(highscores)
		
		self.timer.reset()
		
		self.gameGUI.undraw()
		self.gameGUI.delAll()
		
		halfWinW = self.window.getWidth() // 2
		
		# Tell the user GAME OVER
		gameOverText = Text(Point(halfWinW, 100), "GAME OVER")
		gameOverText.setSize(36)
		
		yourScoreText = Text(Point(halfWinW, 200),
							 f"Your Score: {str(finalScore)} secs.")
		yourScoreText.setSize(20)
		
		# Width: 100, height: 50
		againButton = Button(Point(halfWinW - 50, 425),
							 Point(halfWinW + 50, 475),
							 "blue",
							 "Again?")
		
		def againButtonMouseClick(againButton, mousePoint):
			
			self.newGame()
		
		againButton.mouseClick = MethodType(againButtonMouseClick, againButton)
		
		self.gameGUI.addAll(gameOverText,
						yourScoreText,
						againButton)
		
		# This method will actually draw the game over elements after adding the
		# highscores element
		displayHighscores(highscores,
						  self.gameGUI,
						  self.window,
						  Point(halfWinW, 350))
	
	def playNextSong(self):
		
		# This will either get the song at index 0 (if it's currently the one at index 1)
		# or the song at index -1 == 1 (if it's currently the one at index 0)
		self.currentSong = self.songChoices[self.songChoices.index(self.currentSong) - 1]
		
		self.musicWave = sa.WaveObject.from_wave_file("audio/" + self.currentSong)
		self.musicPlay = self.musicWave.play()

class Obstacle(Image):
	
	UP    = 1
	DOWN  = 2
	LEFT  = 3
	RIGHT = 4
	
	DEFAULT_MIN_T = 250
	DEFAULT_MAX_T = 400
	
	minT: int = DEFAULT_MIN_T
	maxT: int = DEFAULT_MAX_T
	
	def __init__(self, window: GraphWin):
		
		self.window = window
		
		# All images are about 84 pixels high or wide, and something or other
		# Random choice of all filenames within "img" directory
		super().__init__(Point(0, 0), ("img/obs/" + choice(os.listdir("img/obs"))))
		
		# Calculate the points that can define a rectangle around the
		# image as the anchor point is at the direct center of the image,
		# and isn't useful for collision detection.
		self.halfW = (self.getWidth() // 2)
		self.halfH = (self.getHeight() // 2)
		
		# Random time between min and max ticks,
		# rounded to the 3rd decimal place
		self.movementTime = randint(Obstacle.minT, Obstacle.maxT)
		
		# Set the direction to move to be random between moving up (starting at the bottom),
		# moving right (starting from the left), etc.
		self.moveDir = choice([Obstacle.UP, Obstacle.DOWN, Obstacle.LEFT, Obstacle.RIGHT])
		
		match self.moveDir:
			
			case Obstacle.UP:
				# Random position between the window
				self.startX = randint(25, (window.getWidth() - 25 - self.halfW))
				self.startY = window.getHeight()
				# Calculate the # of pixels to move every tick so that
				# it can cross the entire window in the needed time.
				# It accounts for the "overflow" area offscreen (halfH * 3).
				moveAmt = (window.getHeight() + (self.halfH * 3)) / self.movementTime
				self.moveAmtX = 0
				self.moveAmtY = -moveAmt
				
			case Obstacle.DOWN:
				self.startX = randint(25, (window.getWidth() - 25 - self.halfW))
				self.startY = -self.getHeight()
				moveAmt = (window.getHeight() + (self.halfH * 3)) / self.movementTime
				self.moveAmtX = 0
				self.moveAmtY = moveAmt
				
			case Obstacle.LEFT:
				self.startX = window.getWidth()
				self.startY = randint(25, (window.getHeight() - 25 - self.halfH))
				moveAmt = (window.getWidth() + (self.halfW * 3)) / self.movementTime
				self.moveAmtX = -moveAmt
				self.moveAmtY = 0
				
			case Obstacle.RIGHT:
				self.startX = -self.getWidth()
				self.startY = randint(25, (window.getHeight() - 25 - self.halfH))
				moveAmt = (window.getWidth() + (self.halfW * 3)) / self.movementTime
				self.moveAmtX = moveAmt
				self.moveAmtY = 0
		
		self.move(self.startX, self.startY)
	
	def poll(self) -> bool:
		"""
		Moves the obstacle every tick.
		:return: bool: Should be destroyed (finished being an obstacle).
		"""
		
		# Finished moving, so let the game know to destroy the obstacle
		if self.movementTime == 0:
			
			return True
		
		# Move however much is needed
		self.move(self.moveAmtX, self.moveAmtY)
		
		self.p1 = Point(self.getAnchor().getX() - self.halfW,
						self.getAnchor().getY() - self.halfH)
		self.p2 = Point(self.getAnchor().getX() + self.halfW,
						self.getAnchor().getY() + self.halfH)
		
		# Decrement by 1 each tick so that it acts like a timer
		self.movementTime -= 1
		
		return False

class ObstacleHandler:
	
	def __init__(self, window, playerRect: Rectangle):
		
		self.window = window
		self.playerRect = playerRect
		
		self.obstacles = []
	
	def poll(self, timer):
		
		for obs in self.obstacles:
			
			# If the obstacle should be destroyed, destroy it
			if obs.poll():
				obs.undraw()
				self.obstacles.remove(obs)
	
	def sendNewObs(self):
		
		obs = Obstacle(self.window)
		
		obs.draw(self.window)
		
		self.obstacles.append(obs)
	
	def hasCollided(self) -> bool:
		"""Returns True if two obstacles overlap, else False.
		This really checks if the first half of a given rect (by dividing into
		two triangles) overlaps with another, and then checks the second."""
		
		ply_p1x = self.playerRect.getP1().getX()
		ply_p1y = self.playerRect.getP1().getY()
		
		ply_p2x = self.playerRect.getP2().getX()
		ply_p2y = self.playerRect.getP2().getY()
		
		for obs in self.obstacles:
			
			# If ply_p1 is between the image horizontally
			if obs.p1.getX() <= ply_p1x <= obs.p2.getX():
				# And, if ply_p1 is between the image vertically
				if obs.p1.getY() <= ply_p1y <= obs.p2.getY():
					return True
			
			# Same, but for ply_p2
			elif obs.p1.getX() <= ply_p2x <= obs.p2.getX():
				if obs.p1.getY() <= ply_p2y <= obs.p2.getY():
					return True
		
		return False
	
	def destroyAll(self):
		"""Undraw the obstacles"""
		
		for obs in self.obstacles:
			obs.undraw()
		
		self.obstacles.clear()

def _playerRectMouseMove(playerRect, mouse: Point):
	
	pX = playerRect.getP1().getX()
	pY = playerRect.getP1().getY()
	
	mX = mouse.getX()
	mY = mouse.getY()
	
	# Move the difference between the positions, then turn it
	# negative or positive depending on the mouse's position
	x_amt = abs(mX - pX) * (-1 if mX < pX else 1)
	y_amt = abs(mY - pY) * (-1 if mY < pY else 1)
	
	playerRect.move(x_amt - playerRect.halfW,
					y_amt - playerRect.halfH)

def getHighscores() -> list[int]:
	"""Returns a list of highscores (as integers) from highscores.txt"""
	
	# This will handle IO closing implicitly
	with open("data/highscores.txt", "r") as highscoresFile:
		
		# Store the scores as integers in a list,
		# where each saved score is a line-separated integer
		return [int(s) for s in highscoresFile.read().split()]

def displayHighscores(highscores: list, gui, window, point):
	
	highScoresString = "HIGH SCORES\n\n"
	
	# Display only the top three highscores
	# And remove the trailing whitespace too
	for score in ([str(s).rstrip() for s in highscores][0:3]):
		highScoresString += score + " secs.\n"
	
	highScoresText = Text(point, highScoresString)
	highScoresText.setSize(20)
	
	# Undraw the GUI so that the highscores can be added then drawn
	gui.undraw()
	
	gui.addAll(highScoresText)
	
	# highScoresText.draw(window)
	gui.draw(window)
