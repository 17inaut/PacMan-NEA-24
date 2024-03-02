import pygame
from button import Button
from pygame import mixer as m #imports mixer and allows its reference to be 'm' rather than mixer
pygame.init() #INITIALISE PYGAME
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(64)
m.init()
font = pygame.font.Font('Minecraft.ttf', 55)
width = 900
height = 950
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("MAIN MENU")
m.music.load('sounds/Main Menu Music.wav')
m.music.play()
fps = 60
timer = pygame.time.Clock()
pygame.display.flip()
buttonImage = pygame.image.load('miscImages/button.png')
running = True
def drawOther():
    mainMenuTXT = font.render('MAIN MENU', True, 'white')
    screen.blit(mainMenuTXT, (750, 800))

while True:
    playerMousePos = pygame.mouse.get_pos()
    screen.fill('#301934')