# Author: Seamus Boots
# Desc.: Apes Abound is a single-player video game in which the player has to dodge incoming
#        images of apes. The player controls a square on screen by moving their mouse, and a
#        timer will keep track of the amount of time the player has sustained collision,
#        which correlates with their score. The game gets progressively harder over time,
#        in which the time obstacles move across the screen shortens every second. There's a
#        nice GUI for interfacing, and highscores are automatically saved upon a game over.
# Input: The player can use the mouse to click buttons, as well as move the mouse around
#        to control a square. The user can also utilize the escape key for quitting.
# Output: A GUI window is displayed on screen with buttons, text, and images. There is also
#         music which plays in the background.

from game import Game, getHighscores, displayHighscores
from sac_graphics import GraphWin, Point, Text, Image
from gui import GUI, Button
from types import MethodType

def main():
	
	# Set up a 1000x600 window, and prevent it from automatically updating
	# itself, as I will update it manually using a tick system.
	window = GraphWin("Apes Abound", 1000, 600, autoflush=False)
	
	homeGUI = GUI()
	gameGUI = GUI()
	
	# Give the game object pointers to the window & GUI's
	game = Game(window, homeGUI, gameGUI)
	
	halfWinW = window.getWidth() // 2
	
	title = Text(Point(halfWinW, 150), "Apes Abound")
	title.setSize(25)
	
	infoText = Text(Point(200, 365),
					"Objective: Dodge incoming apes \nby moving your mouse around.\n\n" + \
					"To quit at any time, press \nthe escape button.\n\n" + \
					"Scores are automatically saved.")
	infoText.setSize(16)
	
	jamboImage = Image(Point(750, 400), "img/jambo.gif")
	
	jamboText = Text(Point(750, 225), "Meet Jambo")
	jamboText.setSize(15)
	
	# width: 100, height: 50
	startButton = Button(Point(halfWinW - 50, 300),
						 Point(halfWinW + 50, 350),
						 "green",
						 "Start")
	
	def startButtonMouseClick(startButton, mouse: Point):
		
		homeGUI.undraw()
		
		game.newGame()
	
	startButton.mouseClick = MethodType(startButtonMouseClick, startButton)
	
	# width: 100, height: 50
	scoresButton = Button(Point(halfWinW - 50, 400),
							Point(halfWinW + 50, 450),
							"red",
							"Scores")
	
	def scoresButtonMouseClick(scoresButton, mouse: Point):
		
		# Undraw and delete the scores button
		scoresButton.undraw()
		homeGUI.delElem(scoresButton)
		
		# Display the top three highscores
		displayHighscores(getHighscores(),
						  homeGUI,
						  window,
						  Point(halfWinW, 465))
	
	scoresButton.mouseClick = MethodType(scoresButtonMouseClick, scoresButton)
	
	homeGUI.addAll(title,
					infoText,
					jamboImage,
					jamboText,
					startButton,
					scoresButton)
	
	homeGUI.draw(window)
	
	game.gameLoop()

if __name__ == "__main__":
	
	main()
