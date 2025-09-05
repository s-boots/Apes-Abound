# Author: Seamus Boots
# Desc.: This file manages graphical user interface elements.
# Input: User inputs mouse movement and clicks, and key presses.
# Output: Graphic elements are displayed within a window.

from sac_graphics import GraphWin, Point, Rectangle, Text

# The button classes inherits the methods and attributes of Rectangle
class Button(Rectangle):
	
	def __init__(self, p1: Point, p2: Point, color: str, text: str):
		
		super().__init__(p1, p2)
		
		self.setFill(color)
		
		# These flags denote it only needs to handle mouse clicks
		self.hasMouseClick = True
		self.hasMouseMove  = False
		self.hasKeyPress   = False
		
		# This will be the text overlaying it, sized appropriately
		self.textObj = Text(self.getCenter(), text)
		self.textObj.setSize(int((p2.getY() - p1.getY()) * 0.3))
	
	def draw(self, window):
		
		super().draw(window)
		self.textObj.draw(window)
	
	def undraw(self):
		
		super().undraw()
		self.textObj.undraw()

class Timer(Text):
	"""Keeps track of the current tick, and counts the time in seconds"""
	
	def __init__(self, centralPoint: Point):
		
		super().__init__(centralPoint, "")
		
		self.currentTick = 0
		self.time = 0
		
		# The reset() method will set its text
		self.reset()
		self.setSize(25)
	
	def tick(self) -> bool:
		"""
		Increments the tick unless its 100, then it resets to 0
		:return: bool: Whether the tick reached 100 (1 second has passed)
		"""
		
		isTick100 = (self.currentTick == 100)
		
		if isTick100:
			
			self._incSec()
			
			self.currentTick = 0
		
		else:
			
			self.currentTick += 1
		
		return isTick100
	
	def _incSec(self):
		"""Increment the timer by 1 second"""
		self.time += 1
		self.setText(str(self.time) + "s")
	
	def reset(self):
		"""Reset the timer to 0, and set its text."""
		
		# Yes, I'm that guy
		self.time = -1
		self._incSec()
	
	def getTime(self) -> int:
		
		return self.time

class GUI:
	
	def __init__(self):
		
		self.elements = []
		
		self.isVisible = False
		
		# Dummy value to test against new mouse check every poll
		self.lastMP = Point(-1, -1)
	
	def poll(self, key: str, mouse: tuple):
		
		# Only handle input if the GUI is actually visible
		if self.isVisible:
			
			mp = mouse[0]
			isMouseClicked = mouse[1]
			
			for elem in self.elements:
				
				try:
					
					if elem.hasMouseClick:
						if not isMouseClicked:
							return
						
						e_p1 = elem.getP1()
						e_p2 = elem.getP2()
						
						x = mp.getX()
						y = mp.getY()
						
						# If the mouse click was inside the button's area,
						# invoke its event.
						if x > e_p1.getX() and x < e_p2.getX():
							if y > e_p1.getY() and y < e_p2.getY():
								elem.mouseClick(mp)
					
					if elem.hasMouseMove:
						
						# Check if the last mouse point changed positions,
						# and invoke the event if so.
						if (self.lastMP.getX() != mp.getX()) or (self.lastMP.getY() != mp.getY()):
							
							elem.mouseMove(mp)
							
							self.lastMP = mp
				
				# Element cannot be interacted by the user
				except AttributeError:
					
					continue
	
	def draw(self, window: GraphWin):
		
		self.isVisible = True
		
		for elem in self.elements:
			
			elem.draw(window)
	
	def undraw(self):
		
		self.isVisible = False
		
		for elem in self.elements:
			
			elem.undraw()
	
	def addAll(self, *args):
		"""This is fun, it can take as many elements as needed, and adds
		them all in one short loop."""
		
		for elem in args:
			
			elem.parentGUI = self
			
			self.elements.append(elem)
	
	def delAll(self):
		"""Deletes all the elements in a GUI"""
		self.elements.clear()
	
	def delElem(self, elem):
		"""Deletes only the single element provided"""
		self.elements.remove(elem)
