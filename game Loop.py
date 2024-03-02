import pygame, sys
import copy
import math
import random
from button import Button
from boards import boards
from boardForWins import boardForWins
from pygame import mixer as m #imports mixer and allows its reference to be 'm' rather than mixer
pygame.init() #INITIALISE PYGAME
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(64)
m.init()
#defines the dimensions of the screen
width = 900
height = 950
screen = pygame.display.set_mode([width, height])
pygame.display.set_caption("PACMAN")
#runs game at 60 fps, the average frame rate for most games
timer = pygame.time.Clock()
#60 frames displayed per second
fps = 60
font1 = pygame.font.Font('Minecraft.ttf', 20)
font2 = pygame.font.Font('Minecraft.ttf', 55)
font3 = pygame.font.Font('Minecraft.ttf', 80)
#board colour
colour = 'dark gray'
sound = True  # turns the volume on or off
def gameLoop():
    global sound
    # PI is needed for the board
    PI = math.pi
    levelOne = copy.deepcopy(boards)
    winBoard = copy.deepcopy(boardForWins)
    # stores list of allowed turns
    count = 0
    flick = False
    validTurns = [False, False, False, False]
    playerScore = 0
    playerLives = 0
    startupCounter = 0
    moving = False
    intro = m.Sound('sounds/Game Intro.wav')
    if sound:
        intro.play()
    playerLoses = False
    playerWins = False
    # PacMan
    livesDisplay = pygame.transform.scale(pygame.image.load('playerImages/frame2.png').convert_alpha(),
                                          (25, 25))  # stores pacman image for lives
    images = []
    for i in range(1, 3):
        images.append(pygame.transform.scale(pygame.image.load(f'playerImages/frame{i}.png').convert_alpha(),
                                             (40, 40)))  # stores pacman image
    pacman_x = 430  # x position
    pacman_y = 665  # y position
    pacCounter = 0
    pacmanDirection = 1  # where pacman is facing
    pacmanDirectionControl = 1
    pacSpeed = 2  # speed of PacMan
    powerup = False
    powerCount = 0
    powerUPflick = True
    # ghosts
    ghostEaten = [False, False, False, False]
    ghostSpeed = 2
    target_tile = [(pacman_x, pacman_y), (pacman_x, pacman_y), (pacman_x, pacman_y), (pacman_x, pacman_y)]
    # caught ghosts
    scaredBlue = pygame.transform.scale(pygame.image.load('ghostImages/scaredBlue.png').convert_alpha(), (40, 40))
    scaredWhite = pygame.transform.scale(pygame.image.load('ghostImages/scaredWhite.png').convert_alpha(), (40, 40))
    scaredEyes = pygame.transform.scale(pygame.image.load('ghostImages/scaredEyes.png').convert_alpha(), (40, 40))

    # blinky
    blinky_looks = pygame.transform.scale(pygame.image.load('ghostImages/blinky.png').convert_alpha(), (40, 40))
    blinkyDirection = 1  # where blinky is facing
    blinkyXcoord = 430 #360
    blinkyYcoord = 390 #410
    blinkyInBox = False
    blinkyCaught = False

    # inky
    inky_looks = pygame.transform.scale(pygame.image.load('ghostImages/inky.png').convert_alpha(), (40, 40))
    inkyDirection = 3  # where inky is facing
    inkyXcoord = 430
    inkyYcoord = 330
    inkyInBox = False
    inkyCaught = False

    # pinky
    pinky_looks = pygame.transform.scale(pygame.image.load('ghostImages/pinky.png').convert_alpha(), (40, 40))
    pinkyDirection = 3  # where pinky is facing
    pinkyXcoord = 360
    pinkyYcoord = 410
    pinkyInBox = False
    pinkyCaught = False

    # clyde
    clyde_looks = pygame.transform.scale(pygame.image.load('ghostImages/clyde.png').convert_alpha(), (40, 40))
    clydeDirection = 2  # where clyde is facing
    clydeXcoord = 500
    clydeYcoord = 410
    clydeInBox = False
    clydeCaught = False

    class Ghosts:
        def __init__(self, xCoord, yCoord, target, speed, image, direction, caught, inBox, ghostNum):
            self.x = xCoord  # ghost x
            self.y = yCoord  # ghost y
            self.centreX = self.x + 20
            self.centreY = self.y + 20
            self.target = target  # where the ghost needs to go
            self.speed = speed  # depends on game situation
            self.image = image  # ghost own image
            self.direction = direction  # direction based on turnable walls
            self.caught = caught  # boolean for ghost being caught
            self.inBox = inBox  # boolean for ghost in box
            self.ghostNum = ghostNum  # ghost ID
            self.turns, self.inBox = self.collideWallGhosts()  # checks for allowed turns
            self.rect = self.draw()  # ghost rectangle

        def draw(self):
            if playerLoses == False or playerWins == False:
                if (not powerup and not self.caught) or (ghostEaten[
                                                             self.ghostNum] and powerup and not self.caught):  # when there is no powerup and the ghosts are not caught/eaten
                    screen.blit(self.image, (self.x, self.y))  # display original ghost images
                elif powerup and not self.caught and not ghostEaten[
                    self.ghostNum]:  # if there is a powerup but the ghosts are not eaten, display the blue ghost
                    if 420 < powerCount < 450 or 480 < powerCount < 510 or 540 < powerCount < 570:
                        screen.blit(scaredWhite, (self.x, self.y))
                    else:
                        screen.blit(scaredBlue, (self.x, self.y))
                else:
                    screen.blit(scaredEyes, (self.x, self.y))  # if the ghosts are caught display the white ghost

            ghostRect = pygame.rect.Rect((self.centreX - 18, self.centreY - 18), (36,
                                                                                  36))  # building a rectangle to allow the ghosts to have a hitbox to be hit. The purpose of -18 is the make the hit-box smaller so it looks like pacman is actually hitting the ghosts instead of the air around it.
            return ghostRect

        def collideWallGhosts(self):
            num1 = (height - 50) // 32
            num2 = width // 30
            num3 = 16  # fudge number needed so the player hits the actual wall in the tile and not the empty black space in the tile
            self.turns = [False, False, False, False]
            if 0 < self.centreX // 30 < 29:
                if levelOne[(self.centreY - num3) // num1][self.centreX // num2] == 9:
                    self.turns[2] = True
                if self.direction == 1:
                    if levelOne[self.centreY // num1][(self.centreX - num3) // num2] < 3 or (
                            levelOne[self.centreY // num1][(self.centreX - num3) // num2] == 9 and (
                            self.inBox or self.caught)):
                        self.turns[1] = True
                if self.direction == 2:
                    if levelOne[self.centreY // num1][(self.centreX + num3) // num2] < 3 or (
                            levelOne[self.centreY // num1][(self.centreX + num3) // num2] == 9 and (
                            self.inBox or self.caught)):
                        self.turns[0] = True
                if self.direction == 3:
                    if levelOne[(self.centreY + num3) // num1][(self.centreX) // num2] < 3 or (
                            levelOne[(self.centreY + num3) // num1][(self.centreX) // num2] == 9 and (
                            self.inBox or self.caught)):
                        self.turns[3] = True
                if self.direction == 4:
                    if levelOne[(self.centreY - num3) // num1][(self.centreX) // num2] < 3 or (
                            levelOne[(self.centreY - num3) // num1][(self.centreX) // num2] == 9 and (
                            self.inBox or self.caught)):
                        self.turns[2] = True

                if self.direction == 1 or self.direction == 2:  # checks whether ghosts can move up or down
                    if 12 <= self.centreY % num1 <= 18:
                        if levelOne[self.centreY // num1][(self.centreX + num3) // num2] < 3 or (
                                levelOne[self.centreY // num1][(self.centreX + num3) // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[0] = True
                        if levelOne[self.centreY // num1][(self.centreX - num3) // num2] < 3 or (
                                levelOne[self.centreY // num1][(self.centreX - num3) // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[1] = True
                    if 12 <= self.centreX % num2 <= 18:
                        if levelOne[(self.centreY - num3) // num1][self.centreX // num2] < 3 or (
                                levelOne[(self.centreY - num3) // num1][self.centreX // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[2] = True
                        if levelOne[(self.centreY + num3) // num1][self.centreX // num2] < 3 or (
                                levelOne[(self.centreY + num3) // num1][self.centreX // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[3] = True

                if self.direction == 3 or self.direction == 4:  # checks whether ghosts can move up or down
                    if 12 <= self.centreY % num1 <= 18:
                        if levelOne[self.centreY // num1][(self.centreX + num2) // num2] < 3 or (
                                levelOne[self.centreY // num1][(self.centreX + num2) // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[0] = True
                        if levelOne[self.centreY // num1][(self.centreX - num2) // num2] < 3 or (
                                levelOne[self.centreY // num1][(self.centreX - num2) // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[1] = True
                    if 12 <= self.centreX % num2 <= 18:
                        if levelOne[(self.centreY - num3) // num1][self.centreX // num2] < 3 or (
                                levelOne[(self.centreY - num3) // num1][self.centreX // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[2] = True
                        if levelOne[(self.centreY + num3) // num1][self.centreX // num2] < 3 or (
                                levelOne[(self.centreY + num3) // num1][self.centreX // num2] == 9 and (
                                self.inBox or self.caught)):
                            self.turns[3] = True

            else:
                self.turns[0] = True
                self.turns[1] = True
            if 350 < self.x < 550 and 370 < self.y < 480:
                self.inBox = True
            else:
                self.inBox = False

            return self.turns, self.inBox

        def speeding(self):
            if (not powerup and not self.caught) or (ghostEaten[self.ghostNum] and powerup and not self.caught):
                self.speed = 2
            elif powerup and not self.caught and not ghostEaten[self.ghostNum]:
                self.speed = 1
            else:
                self.speed = 4
            return self.speed

        def ghostMovement(self):
            if self.direction == 1:
                if self.target[0] > self.x and self.turns[0]:
                    self.x += self.speed
                elif not self.turns[0]:
                    if self.target[1] > self.y and self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.target[1] < self.y and self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    elif self.target[0] < self.x and self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    elif self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    elif self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                elif self.turns[0]:
                    if self.target[1] > self.y and self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.target[1] < self.y and self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    else:
                        self.x += self.speed
            elif self.direction == 2:
                if self.target[1] > self.y and self.turns[3]:
                    self.direction = 4
                elif self.target[0] < self.x and self.turns[1]:
                    self.x -= self.speed
                elif not self.turns[1]:
                    if self.target[1] > self.y and self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.target[1] < self.y and self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    elif self.target[0] > self.x and self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                    elif self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    elif self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                elif self.turns[1]:
                    if self.target[1] > self.y and self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    if self.target[1] < self.y and self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    else:
                        self.x -= self.speed
            elif self.direction == 3:
                if self.target[0] < self.x and self.turns[1]:
                    self.direction = 2
                    self.x -= self.speed
                elif self.target[1] < self.y and self.turns[2]:
                    self.direction = 3
                    self.y -= self.speed
                elif not self.turns[2]:
                    if self.target[0] > self.x and self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                    elif self.target[0] < self.x and self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    elif self.target[1] > self.y and self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    elif self.turns[3]:
                        self.direction = 4
                        self.y += self.speed
                    elif self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                elif self.turns[2]:
                    if self.target[0] > self.x and self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                    elif self.target[0] < self.x and self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    else:
                        self.y -= self.speed
            elif self.direction == 4:
                if self.target[1] > self.y and self.turns[3]:
                    self.y += self.speed
                elif not self.turns[3]:
                    if self.target[0] > self.x and self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                    elif self.target[0] < self.x and self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    elif self.target[1] < self.y and self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    elif self.turns[2]:
                        self.direction = 3
                        self.y -= self.speed
                    elif self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    elif self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                elif self.turns[3]:
                    if self.target[0] > self.x and self.turns[0]:
                        self.direction = 1
                        self.x += self.speed
                    elif self.target[0] < self.x and self.turns[1]:
                        self.direction = 2
                        self.x -= self.speed
                    else:
                        self.y += self.speed
            if self.x < -30:
                self.x = 900
            elif self.x > 900:
                self.x = -30
            return self.x, self.y, self.direction

        def getTargetsBlinky(self):
            if pacman_x < 450:
                frightenedX = 900  # x coord for ghost to follow when in frightened mode
            else:
                frightenedX = 0  # x coord for ghost to follow when in frightened mode
            if pacman_y < 450:
                frightenedY = 900  # y coord for ghost to follow when in frightened mode
            else:
                frightenedY = 0  # y coord for ghost to follow when in frightened mode
            caught_Target = (400, 380)
            if powerup: #while the powerup is active
                if not self.caught: #if they havem't been caught
                    self.target = (frightenedX, frightenedY) #go here
                else: #otherwise
                    self.target = caught_Target #go here
            else:
                if not self.caught:
                    if 340 < self.x < 560 and 330 < self.y < 480:
                        self.target = (430, 330)
                    else:
                        self.target = (pacman_x, pacman_y)
                else:
                    self.target = caught_Target

            return self.target

        def getTargetsPinky(self):
            if pacman_x < 450:
                frightenedX = 0  # x coord for ghost to follow when in frightened mode
            else:
                frightenedX = 900  # x coord for ghost to follow when in frightened mode
            if pacman_y < 450:
                frightenedY = 900  # y coord for ghost to follow when in frightened mode
            else:
                frightenedY = 0  # y coord for ghost to follow when in frightened mode
            caught_Target = (400, 390)
            if powerup:
                if not self.caught:
                    self.target = (frightenedX, frightenedY)
                else:
                    self.target = caught_Target
            else:
                if not self.caught:
                    if 340 < self.x < 560 and 330 < self.y < 500:
                        self.target = (430, 330)
                    elif not self.caught:
                        if self.direction == 1:
                            self.target = ((pacman_x + 120), pacman_y)
                        elif self.direction == 2:
                            self.target = ((pacman_x - 120), pacman_y)
                        elif self.direction == 3:
                            self.target = (pacman_x, (pacman_y - 120))
                        elif self.direction == 4:
                            self.target = (pacman_x, (pacman_y + 120))
                else:
                    self.target = caught_Target

            return self.target

        def getTargetsClyde(self):
            if pacman_x < 450:
                frightenedX = 900  # x coord for ghost to follow when in frightened mode
            else:
                frightenedX = 0  # x coord for ghost to follow when in frightened mode
            if pacman_y < 450:
                frightenedY = 0  # y coord for ghost to follow when in frightened mode
            else:
                frightenedY = 900  # y coord for ghost to follow when in frightened mode
            caught_Target = (400, 390)
            if powerup:
                if not self.caught:
                    self.target = (frightenedX, frightenedY)
                elif self.inBox:
                    self.target = (430, 330)
                else:
                    self.target = caught_Target
            else:
                if not self.caught:
                    dx = abs(self.x - pacman_x)
                    dy = abs(pacman_y - self.y)
                    if self.inBox:
                        self.target = (430, 330)
                    elif dx > 480 or dy > 480: #if ghost outside 16 tile radius
                        self.target = (pacman_x, pacman_y)
                    else: #if ghost within radius, random movement
                        self.target = ((random.randint((pacman_x - 480), (pacman_x + 480))),
                                       (random.randint((pacman_y - 480), (pacman_y + 480))))
                else:
                    self.target = caught_Target

            return self.target

        def getTargetsInky(self):
            if pacman_x < 450:
                frightenedX = 900  # x coord for ghost to follow when in frightened mode
            else:
                frightenedX = 0  # x coord for ghost to follow when in frightened mode
            if pacman_y < 450:
                frightenedY = 0  # y coord for ghost to follow when in frightened mode
            else:
                frightenedY = 900  # y coord for ghost to follow when in frightened mode
            caught_Target = (400, 390)
            if powerup:
                if not self.caught:  # not caught
                    self.target = (frightenedX, frightenedY)
                elif self.inBox:  # in box during powerup
                    self.target = (430, 300)
                else:  # if caught during powerup
                    self.target = caught_Target
            else:
                if not self.caught:
                    if self.inBox:  # in box
                        self.target = (430, 300)
                    else:
                        dy = abs(pacman_y - self.y)  # difference between pac_y and ghost_y pos
                        dx = abs(pacman_x - self.x)  # difference between pac_x and ghost_x pos
                        if dx < 450:  # dx and pacY
                            self.target = (dx, pacman_y)
                        elif dx > 450:  # pacX and dy
                            self.target = (pacman_x, dy)
                        elif dy > 450:  # pacX and dy
                            self.target = (dx, pacman_y)
                        elif dy < 450:  # dx and pacY
                            self.target = (pacman_x, dy)
                else:
                    self.target = caught_Target
            return self.target

    def loadBoard(lvl):
        num1 = ((height - 50) // 32)  # height of one position
        num2 = (width // 30)  # width of one position
        for i in range(len(lvl)):
            for j in range(len(lvl[i])):
                match lvl[i][j]:
                    case 1:  # small pellets
                        pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
                    case 2 if not flick:  # power pellets
                        pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 8)
                    case 3:  # vertical line border
                        pygame.draw.line(screen, colour, (j * num2 + (0.5 * num2), i * num1),
                                         (j * num2 + (0.5 * num2), i * num1 + num1), 3)
                    case 4:  # horizontal line border
                        pygame.draw.line(screen, colour, (j * num2, i * num1 + (0.5 * num1)),
                                         (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
                    case 5:  # left to down
                        pygame.draw.arc(screen, colour,
                                        [(j * num2 - (0.5 * num2)), (i * num1 + (0.5 * num1)), num2, num1], 0, PI / 2,
                                        3)
                    case 6:  # down to right
                        pygame.draw.arc(screen, colour,
                                        [(j * num2 + (0.5 * num2)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI,
                                        3)
                    case 7:  # up to right
                        pygame.draw.arc(screen, colour,
                                        [(j * num2 + (0.5 * num2)), (i * num1 - (0.5 * num1)), num2, num1], PI,
                                        (PI * 3) / 2, 3)
                    case 8:  # left to up
                        pygame.draw.arc(screen, colour,
                                        [(j * num2 - (0.5 * num2)), (i * num1 - (0.5 * num1)), num2, num1],
                                        (PI * 3) / 2, 0, 3)
                    case 9:  # horizontal line border
                        pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                         (j * num2 + num2, i * num1 + (0.5 * num1)), 6)

    def loadPacman():
        match pacmanDirection:
            case 1:  # right
                screen.blit(images[pacCounter // 15], (pacman_x, pacman_y))
            case 2:  # left
                screen.blit(pygame.transform.rotate(images[pacCounter // 15], 180), (pacman_x, pacman_y))
            case 3:  # up
                screen.blit(pygame.transform.rotate(images[pacCounter // 15], 90), (pacman_x, pacman_y))
            case 4:  # down
                screen.blit(pygame.transform.rotate(images[pacCounter // 15], 270), (pacman_x, pacman_y))

    def collideWall(x, y):  # passes PacMan's centre values
        turns = [False, False, False, False]
        num1 = (height - 50) // 32
        num2 = width // 30
        num3 = 16  # fudge number needed so the player hits the actual wall in the tile and not the empty black space in the tile
        # check collisions based on the centre coordinates of PacMan and the fudge number
        if x // 30 < 29:  # Tiles are from 0 to 29 px #this if statement checks if you can turn back the way you came from
            if pacmanDirection == 1:
                if levelOne[y // num1][
                    (x - num3) // num2] < 3:  # checks if the tile right behind PacMan is 0, 1 or 2 when facing right
                    turns[1] = True
            if pacmanDirection == 2:
                if levelOne[y // num1][
                    (x + num3) // num2] < 3:  # checks if the tile right behind PacMan is 0, 1 or 2 when facing left
                    turns[0] = True
            if pacmanDirection == 3:
                if levelOne[(y + num3) // num1][
                    x // num2] < 3:  # checks if the tile right behind PacMan is 0, 1 or 2 when facing up
                    turns[3] = True
            if pacmanDirection == 4:
                if levelOne[(y - num3) // num1][
                    x // num2] < 3:  # checks if the tile right behind PacMan is 0, 1 or 2 when facing down
                    turns[2] = True

            if pacmanDirection == 1 or pacmanDirection == 2:  # checks whether PacMan can move right or left right
                if 12 <= y % num1 <= 18:  # this checks if PacMan is at the midpoint of a tile and only allows PacMan to turn if he is within these pixels
                    if levelOne[y // num1][(x + num3) // num2] < 3:  # checks if tile in front of PacMan is clear
                        turns[0] = True
                    if levelOne[y // num1][(x - num3) // num2] < 3:  # checks if tile behind PacMan is clear
                        turns[1] = True
                if 12 <= x % num2 <= 18:  # this checks if PacMan is at the midpoint of a tile and only allows PacMan to turn if he is within these pixels
                    if levelOne[(y - num1) // num1][x // num2] < 3:
                        turns[2] = True
                    if levelOne[(y + num1) // num1][x // num2] < 3:
                        turns[3] = True

            if pacmanDirection == 3 or pacmanDirection == 4:  # checks whether PacMan can move up or down
                if 12 <= y % num1 <= 18:  # this checks if PacMan is at the midpoint of a tile and only allows PacMan to turn if he is within these pixels
                    if levelOne[y // num1][(x + num2) // num2] < 3:  # checks if tile in front of PacMan is clear
                        turns[0] = True
                    if levelOne[y // num1][(x - num2) // num2] < 3:  # checks if tile behind PacMan is clear
                        turns[1] = True
                if 12 <= x % num2 <= 18:  # this checks if PacMan is at the midpoint of a tile and only allows PacMan to turn if he is within these pixels
                    if levelOne[(y - num3) // num1][x // num2] < 3:
                        turns[2] = True
                    if levelOne[(y + num3) // num1][x // num2] < 3:
                        turns[3] = True

        else:
            turns[0] = True
            turns[1] = True
        return turns

    def collidePellet(score, powerUP, powerUPcounter, eatenGhosts):
        global sound
        num1 = (height - 50) // 32
        num2 = width // 30
        chompSound = m.Sound('sounds/Chomp.wav')
        if 0 < pacman_x < 870:  # ensures indexing is not out of range
            match levelOne[pacmanCentreY // num1][pacmanCentreX // num2]:
                case 1:
                    levelOne[pacmanCentreY // num1][pacmanCentreX // num2] = 0
                    del winBoard[0]
                    score += 10
                    if sound:
                        chompSound.play()
                case 2:
                    # powerChomp.stop()
                    levelOne[pacmanCentreY // num1][pacmanCentreX // num2] = 0
                    del winBoard[0]
                    score += 50
                    powerUP = True
                    powerUPcounter = 0  # resets power up counter to zero if you eat a powerup dot within the timer
                    eatenGhosts = [False, False, False, False]
                    # powerChomp.play(38)
        return score, powerUP, powerUPcounter, eatenGhosts

    def movePacMan(playerXpos, playerYpos):
        match pacmanDirection:
            case 1 if validTurns[0]:
                playerXpos += pacSpeed
            case 2 if validTurns[1]:
                playerXpos -= pacSpeed
            case 3 if validTurns[2]:
                playerYpos -= pacSpeed
            case 4 if validTurns[3]:
                playerYpos += pacSpeed

        return playerXpos, playerYpos

    def drawOther():
        restartTXT = font2.render('Press SPACEBAR to restart', True, 'white')
        menuTXT = font2.render('Press ESC for menu', True, 'white')
        scoreText = font1.render(f'score : {playerScore}', True, 'white')
        screen.blit(scoreText, (750, 922))
        xCoord = 10
        for i in range(playerLives + 1):
            screen.blit(livesDisplay, (xCoord, 918))
            xCoord += 30
        if powerup and powerUPflick:
            pygame.draw.circle(screen, (36, 4, 252), (135, 932), 15)
        elif powerup and not powerUPflick:
            pygame.draw.circle(screen, 'white', (135, 932), 12)
        if playerLoses:
            screen.fill('black')
            pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
            pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
            playerLosesTXT = font2.render('Game Over', True, 'white')
            screen.blit(scoreText, (50, 50))
            screen.blit(playerLosesTXT, (290, 250))
            screen.blit(restartTXT, (80, 330))
            screen.blit(menuTXT, (200, 410))
        if playerWins:
            m.music.load('sounds/Player Wins.mp3')
            if sound:
                m.music.play()
            screen.fill('black')
            pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
            pygame.draw.rect(screen, 'gray', [70, 220, 760, 260], 0, 10)
            playerwinsTXT = font2.render('WINNER', True, 'white')
            screen.blit(scoreText, (50, 50))
            screen.blit(playerwinsTXT, (330, 250))
            screen.blit(restartTXT, (80, 330))
            screen.blit(menuTXT, (200, 410))

    # runs main event loop
    runningGame = True
    # main event loop
    while runningGame:
        timer.tick(fps)
        if powerup and powerCount < 600:
            powerCount += 1
            if 420 < powerCount < 450 or 480 < powerCount < 510 or 540 < powerCount < 570:
                powerUPflick = False
            else:
                powerUPflick = True
        elif powerup and powerCount >= 600:
            powerCount = 0
            powerup = False
            ghostEaten = [False, False, False, False]
        if startupCounter < 250 and not playerLoses and not playerWins:
            startupCounter += 1
            moving = False
            pacSpeed = 0
        else:
            moving = True
            pacSpeed = 2
        screen.fill('black')
        loadBoard(levelOne)
        pacmanCentreX = pacman_x + 20
        pacmanCentreY = pacman_y + 20
        pacCircle = pygame.draw.circle(screen, 'black', (pacmanCentreX, pacmanCentreY), 22, 2)
        drawOther()
        if len(winBoard) == 0:
            playerWins = True
            moving = False
            startupCounter = 0
            if playerWins == True:
                m.music.load('sounds/Player Wins.mp3')
                if sound:
                    m.music.play()
                powerup = False
                # ghostEaten = [False, False, False, False]
                blinkyCaught = False
                inkyCaught = False
                pinkyCaught = False
                clydeCaught = False
                pacSpeed = 0
                ghostSpeed = 0
                pacmanDirectionControl = 1
                pacmanDirection = 1
                pacman_x = 430
                pacman_y = 515
                blinkyDirection = 0
                blinkyXcoord = 140
                blinkyYcoord = 900
                inkyDirection = 0
                inkyXcoord = 320
                inkyYcoord = 900
                pinkyDirection = 0
                pinkyXcoord = 520
                pinkyYcoord = 900
                clydeDirection = 0
                clydeXcoord = 700
                clydeYcoord = 900
        else:
            playerWins = False
        loadPacman()
        blinky = Ghosts(blinkyXcoord, blinkyYcoord, target_tile[0], ghostSpeed, blinky_looks, blinkyDirection,
                        blinkyCaught, blinkyInBox, 0)
        inky = Ghosts(inkyXcoord, inkyYcoord, target_tile[1], ghostSpeed, inky_looks, inkyDirection, inkyCaught,
                      inkyInBox, 1)
        pinky = Ghosts(pinkyXcoord, pinkyYcoord, target_tile[2], ghostSpeed, pinky_looks, pinkyDirection, pinkyCaught,
                       pinkyInBox, 2)
        clyde = Ghosts(clydeXcoord, clydeYcoord, target_tile[3], ghostSpeed, clyde_looks, clydeDirection, clydeCaught,
                       clydeInBox, 3)
        blinky.speeding()
        inky.speeding()
        pinky.speeding()
        clyde.speeding()
        blinky.getTargetsBlinky()
        inky.getTargetsInky()
        pinky.getTargetsPinky()
        clyde.getTargetsClyde()
        if moving:
            if pacCounter < 29:
                pacCounter += 1
            else:
                pacCounter = 0
            if count < 41:
                count += 1
                if count > 20:
                    flick = False
            else:
                count = 0
                flick = True
            validTurns = collideWall(pacmanCentreX, pacmanCentreY)
            blinkyXcoord, blinkyYcoord, blinkyDirection = blinky.ghostMovement()
            inkyXcoord, inkyYcoord, inkyDirection = inky.ghostMovement()
            pinkyXcoord, pinkyYcoord, pinkyDirection = pinky.ghostMovement()
            clydeXcoord, clydeYcoord, clydeDirection = clyde.ghostMovement()
        pacman_x, pacman_y = movePacMan(pacman_x, pacman_y)
        playerScore, powerup, powerCount, ghostEaten = collidePellet(playerScore, powerup, powerCount, ghostEaten)
        pacChomp = m.Sound('sounds/Caught PacMan.wav')
        ghostChomp = m.Sound('sounds/Ghost Caught.wav')

        if not powerup:
            if ((pacCircle.colliderect(blinky.rect) and not blinky.caught) or (pacCircle.colliderect(inky.rect) and not inky.caught) or
                    (pacCircle.colliderect(clyde.rect) and not clyde.caught) or (pacCircle.colliderect(pinky.rect) and not pinky.caught)):
                if playerLives > 0:
                    if sound:
                        pacChomp.play()
                    playerLives -= 1
                    startupCounter = 0
                    pacman_x = 430  # x position
                    pacman_y = 665  # y position
                    pacCounter = 0
                    pacmanDirection = 1  # where pacman is facing
                    pacmanDirectionControl = 1
                    pacSpeed = 2  # speed of PacMan
                    powerup = False
                    powerCount = 0
                    powerUPflick = True
                    blinkyDirection = 1  # where blinky is facing
                    blinkyXcoord = 430
                    blinkyYcoord = 390
                    blinkyCaught = False
                    inkyDirection = 3  # where inky is facing
                    inkyXcoord = 430
                    inkyYcoord = 330
                    inkyCaught = False
                    pinkyDirection = 3  # where pinky is facing
                    pinkyXcoord = 360
                    pinkyYcoord = 410
                    pinkyCaught = False
                    clydeDirection = 2  # where clyde is facing
                    clydeXcoord = 500
                    clydeYcoord = 410
                    clydeCaught = False
                    ghostEaten = [False, False, False, False]
                else:
                    playerLoses = True
                    moving = False
                    powerup = False
                    startupCounter = 0
                    ghostEaten = [False, False, False, False]
                    if playerLoses:
                        m.music.load('sounds/Player Loses.mp3')
                        if sound:
                            m.music.play()
                        pacSpeed = 0
                        ghostSpeed = 0
                        pacmanDirectionControl = 1
                        pacmanDirection = 1
                        pacman_x = 430
                        pacman_y = 515
                        blinkyDirection = 0
                        blinkyXcoord = 140
                        blinkyYcoord = 900
                        inkyDirection = 0
                        inkyXcoord = 320
                        inkyYcoord = 900
                        pinkyDirection = 0
                        pinkyXcoord = 520
                        pinkyYcoord = 900
                        clydeDirection = 0
                        clydeXcoord = 700
                        clydeYcoord = 900
        if powerup and pacCircle.colliderect(blinky.rect) and ghostEaten[0] and not blinky.caught:
            if playerLives > 0:
                playerLives -= 1
                startupCounter = 0
                pacman_x = 430  # x position
                pacman_y = 665  # y position
                pacCounter = 0
                pacmanDirection = 1  # where pacman is facing
                pacmanDirectionControl = 1
                pacSpeed = 2  # speed of PacMan
                powerup = False
                powerCount = 0
                powerUPflick = True
                blinkyDirection = 1  # where blinky is facing
                blinkyXcoord = 430
                blinkyYcoord = 390
                blinkyCaught = False
                inkyDirection = 3  # where inky is facing
                inkyXcoord = 430
                inkyYcoord = 330
                inkyCaught = False
                pinkyDirection = 3  # where pinky is facing
                pinkyXcoord = 360
                pinkyYcoord = 410
                pinkyCaught = False
                clydeDirection = 2  # where clyde is facing
                clydeXcoord = 500
                clydeYcoord = 410
                clydeCaught = False
                ghostEaten = [False, False, False, False]
            else:
                playerLoses = True
                moving = False
                startupCounter = 0
        if powerup and pacCircle.colliderect(inky.rect) and ghostEaten[1] and not inky.caught:
            if playerLives > 0:
                playerLives -= 1
                startupCounter = 0
                pacman_x = 430  # x position
                pacman_y = 665  # y position
                pacCounter = 0
                pacmanDirection = 1  # where pacman is facing
                pacmanDirectionControl = 1
                pacSpeed = 2  # speed of PacMan
                powerup = False
                powerCount = 0
                powerUPflick = True
                blinkyDirection = 1  # where blinky is facing
                blinkyXcoord = 430
                blinkyYcoord = 390
                blinkyCaught = False
                inkyDirection = 3  # where inky is facing
                inkyXcoord = 430
                inkyYcoord = 330
                inkyCaught = False
                pinkyDirection = 3  # where pinky is facing
                pinkyXcoord = 360
                pinkyYcoord = 410
                pinkyCaught = False
                clydeDirection = 2  # where clyde is facing
                clydeXcoord = 500
                clydeYcoord = 410
                clydeCaught = False
                ghostEaten = [False, False, False, False]
            else:
                playerLoses = True
                moving = False
                startupCounter = 0
        if powerup and pacCircle.colliderect(pinky.rect) and ghostEaten[2] and not pinky.caught:
            if playerLives > 0:
                playerLives -= 1
                startupCounter = 0
                pacman_x = 430  # x position
                pacman_y = 665  # y position
                pacCounter = 0
                pacmanDirection = 1  # where pacman is facing
                pacmanDirectionControl = 1
                pacSpeed = 2  # speed of PacMan
                powerup = False
                powerCount = 0
                powerUPflick = True
                blinkyDirection = 1  # where blinky is facing
                blinkyXcoord = 430
                blinkyYcoord = 390
                blinkyCaught = False
                inkyDirection = 3  # where inky is facing
                inkyXcoord = 430
                inkyYcoord = 330
                inkyCaught = False
                pinkyDirection = 3  # where pinky is facing
                pinkyXcoord = 360
                pinkyYcoord = 410
                pinkyCaught = False
                clydeDirection = 2  # where clyde is facing
                clydeXcoord = 500
                clydeYcoord = 410
                clydeCaught = False
                ghostEaten = [False, False, False, False]
            else:
                playerLoses = True
                moving = False
                startupCounter = 0
        if powerup and pacCircle.colliderect(clyde.rect) and ghostEaten[3] and not clyde.caught:
            if playerLives > 0:
                playerLives -= 1
                startupCounter = 0
                pacman_x = 430  # x position
                pacman_y = 665  # y position
                pacCounter = 0
                pacmanDirection = 1  # where pacman is facing
                pacmanDirectionControl = 1
                pacSpeed = 2  # speed of PacMan
                powerup = False
                powerCount = 0
                powerUPflick = True
                blinkyDirection = 1  # where blinky is facing
                blinkyXcoord = 430
                blinkyYcoord = 390
                blinkyCaught = False
                inkyDirection = 3  # where inky is facing
                inkyXcoord = 430
                inkyYcoord = 330
                inkyCaught = False
                pinkyDirection = 3  # where pinky is facing
                pinkyXcoord = 360
                pinkyYcoord = 410
                pinkyCaught = False
                clydeDirection = 2  # where clyde is facing
                clydeXcoord = 500
                clydeYcoord = 410
                clydeCaught = False
                ghostEaten = [False, False, False, False]
            else:
                playerLoses = True
                moving = False
                startupCounter = 0
        if (powerup and pacCircle.colliderect(blinky.rect) and not blinky.caught
                and not ghostEaten[0] and not (playerLoses or playerWins)):
            if sound:
                ghostChomp.play()
            blinkyCaught = True
            ghostEaten[0] = True
            playerScore += (2 ** ghostEaten.count(True)) * 100
        if (powerup and pacCircle.colliderect(inky.rect) and not inky.caught
                and not ghostEaten[1] and not (playerLoses or playerWins)):
            if sound:
                ghostChomp.play()
            inkyCaught = True
            ghostEaten[1] = True
            playerScore += (2 ** ghostEaten.count(True)) * 100
        if (powerup and pacCircle.colliderect(pinky.rect) and not pinky.caught
                and not ghostEaten[2] and not (playerLoses or playerWins)):
            if sound:
                ghostChomp.play()
            pinkyCaught = True
            ghostEaten[2] = True
            playerScore += (2 ** ghostEaten.count(True)) * 100
        if (powerup and pacCircle.colliderect(clyde.rect) and not clyde.caught
                and not ghostEaten[3] and not (playerLoses or playerWins)):
            if sound:
                ghostChomp.play()
            clydeCaught = True
            ghostEaten[3] = True
            playerScore += (2 ** ghostEaten.count(True)) * 100

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runningGame = False
            if event.type == pygame.KEYDOWN:
                match event.key:
                    # right-handed movement
                    case pygame.K_RIGHT:
                        pacmanDirectionControl = 1
                    case pygame.K_LEFT:
                        pacmanDirectionControl = 2
                    case pygame.K_UP:
                        pacmanDirectionControl = 3
                    case pygame.K_DOWN:
                        pacmanDirectionControl = 4
                    # left-handed movement
                    case pygame.K_d:
                        pacmanDirectionControl = 1
                    case pygame.K_a:
                        pacmanDirectionControl = 2
                    case pygame.K_w:
                        pacmanDirectionControl = 3
                    case pygame.K_s:
                        pacmanDirectionControl = 4
                #return to main menu
                if event.key == pygame.K_ESCAPE:
                    if sound:
                        m.music.stop()
                        intro.stop()
                    runningGame = False
                    mainMenu()
                # restart game
                if event.key == pygame.K_SPACE:
                    playerLives -= 1
                    startupCounter = 0
                    pacman_x = 430  # x position
                    pacman_y = 665  # y position
                    pacCounter = 0
                    pacmanDirection = 1  # where pacman is facing
                    pacmanDirectionControl = 1
                    pacSpeed = 2  # speed of PacMan
                    powerup = False
                    powerCount = 0
                    powerUPflick = True
                    blinkyDirection = 1  # where blinky is facing
                    blinkyXcoord = 430
                    blinkyYcoord = 390
                    blinkyCaught = False
                    inkyDirection = 3  # where inky is facing
                    inkyXcoord = 430
                    inkyYcoord = 330
                    inkyCaught = False
                    pinkyDirection = 3  # where pinky is facing
                    pinkyXcoord = 360
                    pinkyYcoord = 410
                    pinkyCaught = False
                    clydeDirection = 2  # where clyde is facing
                    clydeXcoord = 500
                    clydeYcoord = 410
                    clydeCaught = False
                    ghostEaten = [False, False, False, False]
                    playerLives = 2
                    playerScore = 0
                    playerWins = False
                    playerLoses = False
                    m.music.unload()
                    levelOne = copy.deepcopy(boards)
                    winBoard = copy.deepcopy(boardForWins)
                    m.music.load('sounds/Game Intro.wav')
                    m.music.play()

            if event.type == pygame.KEYUP:
                match event.key, pacmanDirectionControl:
                    # right handed movement
                    case (pygame.K_RIGHT, 1):
                        pacmanDirectionControl = pacmanDirection
                    case (pygame.K_LEFT, 2):
                        pacmanDirectionControl = pacmanDirection
                    case (pygame.K_UP, 3):
                        pacmanDirectionControl = pacmanDirection
                    case (pygame.K_DOWN, 4):
                        pacmanDirectionControl = pacmanDirection
                    # left handed movement
                    case (pygame.K_d, 1):
                        pacmanDirectionControl = pacmanDirection
                    case (pygame.K_a, 2):
                        pacmanDirectionControl = pacmanDirection
                    case (pygame.K_w, 3):
                        pacmanDirectionControl = pacmanDirection
                    case (pygame.K_s, 4):
                        pacmanDirectionControl = pacmanDirection

        match pacmanDirectionControl:
            case 1 if validTurns[0]:
                pacmanDirection = 1
            case 2 if validTurns[1]:
                pacmanDirection = 2
            case 3 if validTurns[2]:
                pacmanDirection = 3
            case 4 if validTurns[3]:
                pacmanDirection = 4

        # resets PacMan x pos if he leaves screen
        if pacman_x > 900:
            pacman_x = -47
        elif pacman_x < -48:
            pacman_x = 897

        if blinkyCaught and blinky.inBox:
            blinkyCaught = False
            blinkyDirection = 1
        if inkyCaught and inky.inBox:
            inkyCaught = False
            inkyDirection = 3
        if pinkyCaught and pinky.inBox:
            pinkyCaught = False
            pinkyDirection = 3
        if clydeCaught and clyde.inBox:
            clydeCaught = False
            clydeDirection = 2

        # updates entire screen
        pygame.display.flip()
def mainMenu():
    global sound
    m.music.load('sounds/Main Menu Music.wav')
    if sound :
        m.music.play()
    while True:
        screen.fill('black')
        menuMousePos = pygame.mouse.get_pos()

        menuTXT = font3.render("MAIN MENU", True, "White")
        menuRect = menuTXT.get_rect(center=(450, 80))

        playButton = Button(pygame.image.load("miscImages/Play Button.png"), 450, 250,
                            "PLAY", font2, "#fedd00", "White")
        optionsButton = Button(pygame.image.load("miscImages/Options Button.png"), 450, 400,
                               "OPTIONS", font2, "#fedd00","White")
        quitButton = Button(pygame.image.load("miscImages/Quit Button.png"), 450, 550,
                            "QUIT", font2, "#fedd00", "White")

        screen.blit(menuTXT, menuRect)

        for button in [playButton, optionsButton, quitButton]:
            button.changeColour(menuMousePos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if playButton.checkInput(menuMousePos):
                    m.music.stop()
                    gameLoop()
                elif optionsButton.checkInput(menuMousePos):
                    options()
                elif quitButton.checkInput(menuMousePos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
def options():
    global sound
    m.music.load('sounds/Options Music.wav')
    if sound:
        m.music.play()
    while True:
        optionsMousePos = pygame.mouse.get_pos()
        screen.fill("white")
        optionsTXT = font3.render("OPTIONS", True, "Black")
        optionsRect = optionsTXT.get_rect(center=(450, 80))
        screen.blit(optionsTXT, optionsRect)

        soundButton = Button(pygame.image.load('miscImages/Options Button.png'), 450, 400,
                             'SOUND', font2, '#fedd00', 'White')
        optionsBack = Button(pygame.image.load('miscImages/Quit Button.png'), 450, 250,
                             "MENU", font2, "#fedd00", "White")
        quitButton = Button(pygame.image.load("miscImages/Quit Button.png"), 450, 550,
                            "QUIT", font2, "#fedd00", "White")
        optionsBack.changeColour(optionsMousePos)
        optionsBack.update(screen)
        soundButton.changeColour(optionsMousePos)
        soundButton.update(screen)
        quitButton.changeColour(optionsMousePos)
        quitButton.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if optionsBack.checkInput(optionsMousePos):
                    mainMenu()
                elif quitButton.checkInput(optionsMousePos):
                    pygame.quit()
                    sys.exit()
                elif soundButton.checkInput(optionsMousePos) and sound == True:
                    sound = False
                    m.music.stop()
                elif soundButton.checkInput(optionsMousePos) and sound == False:
                    sound = True
                    m.music.play()

        pygame.display.flip()
mainMenu()