import pygame
pygame.init()
class Button():
	def __init__(self, buttonIMG, xCoord, yCoord, inputTXT, font, baseColour, hoverColour):
		self.buttonIMG = buttonIMG
		self.xCoord = xCoord
		self.yCoord = yCoord
		self.font = font
		self.baseColour, self.hoverColour = baseColour, hoverColour
		self.inputTXT = inputTXT
		self.text = self.font.render(self.inputTXT, True, self.baseColour)
		if self.buttonIMG is None: #if there is no value in the buttonIMG
			self.buttonIMG = self.text
		self.rect = self.buttonIMG.get_rect(center=(self.xCoord, self.yCoord))
		self.textRect = self.text.get_rect(center=(self.xCoord, self.yCoord))

	def update(self, screen): #draws button image and text on screen
		if self.buttonIMG is not None: #if available
			screen.blit(self.buttonIMG, self.rect)
		screen.blit(self.text, self.textRect)
	def checkInput(self, position): #if the click is inside the button it is true, otherwise it is false
		if (position[0] in range(self.rect.left, self.rect.right)
				and position[1] in range(self.rect.top, self.rect.bottom)):
			return True
		return False
	def changeColour(self, position): #if hovered over, updates to hover colour, else base colour
		if (position[0] in range(self.rect.left, self.rect.right)
				and position[1] in range(self.rect.top, self.rect.bottom)):
			self.text = self.font.render(self.inputTXT, True, self.hoverColour)
		else:
			self.text = self.font.render(self.inputTXT, True, self.baseColour)