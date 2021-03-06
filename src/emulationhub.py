#! /usr/bin/env python

#
# IMPORT SECTION
#
import pygame, math, sys, subprocess
from pygame.locals import *
from pygame import Surface, draw, transform
from subprocess import check_output
import evdev


pygame.init()
myfont = pygame.font.Font('fonts/Roboto-Regular.ttf', 40)

#
# INIT JOYSTICKS/GAMEPADS
#
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
if len(joysticks)>0: joysticks[0].init()

#
# GET PRIMARY DISPLAY RESOLUTION
# resolution [ x, y, x/2, y/2 ]
#
#xrandr_out = subprocess.check_output('xrandr').split()
#resolution = [int(s) for s in xrandr_out[xrandr_out.index('primary') + 1].replace('+','x').split('x') if s.isdigit()]
resolution = [1680,1024,0,0]
resolution[2] = resolution[0]/2
resolution[3] = resolution[1]/2

screen = pygame.display.set_mode((resolution[0],resolution[1]),pygame.NOFRAME)
#screen = pygame.display.set_mode((resolution[0],resolution[1]))

#
# CLASSES
#
def grayscale_image(surf): 
    width, height = surf.get_size() 
    for x in range(width): 
	for y in range(height): 
    	    red, green, blue, alpha = surf.get_at((x, y)) 
    	    L = 0.3 * red + 0.59 * green + 0.11 * blue 
    	    gs_color = (L, L, L, alpha) 
    	    surf.set_at((x, y), gs_color) 
    return surf 


class Emulator:

    def __init__(self, short, name, command = '', extensions = []):
	self.short = str(short)
	self.name = str(name)
	self.x = self.y = 0
        self.image = pygame.image.load('images/'+self.short+'.png')
	self.width = self.image.get_width()
	self.height = self.image.get_height()
	self.scale = 0.6
	self.image_smoothscale = pygame.transform.scale(grayscale_image(self.image), (int(self.width*self.scale),int(self.height*self.scale)))
	self.active = 1
	self.command = str(command)
	self.games = 0
	self.extensions = extensions

    def set_short(self, short):
	self.short = str(short)
    def get_short(self):
	return(self.short)

    def set_name(self, name):
	self.name = str(name)
    def get_name(self):
	return(self.name)

    def set_command(self, command):
	self.command = str(command)
    def get_command(self):
	return(self.command)

    def set_games(self, games):
	self.games = int(games)
    def get_games(self):
	return(self.games)

    def set_position(self, (x,y)):
        self.x = int(x)
        self.y = int(y)
    def get_position(self):
        return(self.x, self.y)

    def get_height(self, scale = 0):
	if (scale == 0): factor = 1
	else: factor = self.scale
        return(int(self.height*factor))
    def get_width(self, scale = 0):
	if (scale == 0): factor = 1
	else: factor = self.scale
        return(int(self.width*factor))

    def set_scale(self, scale):
	if (self.scale != scale):
    	    self.scale = float(scale)
	    self.image_smoothscale = pygame.transform.scale(grayscale_image(self.image), (int(self.image.get_width()*scale),int(self.image.get_height()*scale)))
    def get_scale(self):
        return(self.scale)

    def set_active(self, active):
        self.active = int(active)
    def get_active(self):
        return(self.active)

    def draw(self, screen, scale = 0):
        if ((self.x<=resolution[0]) & (self.x>=-self.get_width(scale))):
	    if (scale == 0):
		screen.blit(self.image, (self.x, self.y))
	    elif (scale == 1):
		screen.blit(self.image_smoothscale, (self.x, self.y))


def AAfilledRoundedRect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)
    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = Surface(rect.size,SRCALPHA)

    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)
#
# END CLASSES
#

#
# DRAW BACKGROUND
#
background = pygame.image.load('images/wallpaper-3.jpg')
background = pygame.transform.scale(background, (resolution[0],resolution[1]))
pygame.draw.rect(background,(255,255,255),(0,(resolution[3])-130,resolution[0],260))
pygame.draw.rect(background,(63,63,63),(0,(resolution[3])-135,resolution[0],5))
pygame.draw.rect(background,(63,63,63),(0,(resolution[3])+130,resolution[0],5))
screen.blit(background, (0,0))

help_middle = pygame.Surface((resolution[0],55), pygame.SRCALPHA)
help_middle.fill((255,255,255,128))

#
# GENERATE EMULATOR LIST (+SORT +ROTATE_DEF)
#
def rotate(list, direction):
    if (direction == 'right'):
	return list[1:] + list[:1]
    elif (direction == 'left'):
	return list[-1:] + list[:-1]
    else:
	return list

emulator_romdir = 'roms'
emulator_list = []
emulator_list.append (Emulator('dragon32','Dragon 32/64','/usr/bin/xroar -fs -extbas BIOS/d32.rom roms/dragon32/Empire.cas',['cas','wav','bas','asc']))
emulator_list.append (Emulator('amiga','Amiga','/opt/bin/amiga-emulator',[]))
emulator_list.append (Emulator('gb','GameBoy','/opt/bin/gameboy-emulator',[]))
emulator_list.append (Emulator('atari2600','Atari 2600','/usr/bin/stella roms/atari2600/SpaceInvaders.a26',[]))
emulator_list.append (Emulator('3do','3do','/opt/bin/3do-emulator',[]))
emulator_list.append (Emulator('amstradcpc','Amdtrad CPC','/opt/bin/amstradcpc-emulator',[]))

emulator_selection = []
for i, val in enumerate(emulator_list):
    if (val.get_active()): emulator_selection.append([i,val.get_name()])
emulator_selection = sorted(emulator_selection, key=lambda k: k[1]) 
emulator_selection = rotate(emulator_selection,'left')

#
# OTHERS
#
clock = pygame.time.Clock()
BLACK = (0,0,0)
x = down = roll = 0
distancia = 2
aceleracion = 64
factor = 1.8

if len(joysticks)>0: device = evdev.InputDevice('/dev/input/event4')

while 1:
    # USER INPUT
    clock.tick(30)
    for event in pygame.event.get():
        if not hasattr(event, 'key'): continue
        if (event.key==K_RIGHT and event.type==KEYDOWN): roll = 2
        elif (event.key==K_LEFT and event.type==KEYDOWN): roll = 1
        elif (event.key==K_ESCAPE and event.type==KEYDOWN): sys.exit(0)
        elif (event.key==K_RETURN and event.type==KEYDOWN):
	    p = subprocess.Popen("exec " + emulator_list[0].get_command(),stdout=subprocess.PIPE,shell=True)
        elif (event.key==K_TAB and event.type==KEYDOWN):
	    p = subprocess.Popen("exec " + emulator_list[3].get_command(),stdout=subprocess.PIPE,shell=True)
        elif (event.key==K_TAB and event.type==KEYDOWN):
	    p.terminate()

    if 'device' in locals():
	if (device.active_keys() == [314,315]):
	    p.terminate()
	print device.active_keys()
    
    if hasattr(event, 'key'):
	pygame.draw.rect(screen,(255,255,255),(0,(resolution[3])-130,resolution[0],260))
	screen.blit(background, (0,0)) # remove when label test ends

    if (roll == 1): # LEFT
	emulator_selection = rotate(emulator_selection,'left')
	roll = 0
    elif (roll == 2): # RIGHT
	emulator_selection = rotate(emulator_selection,'right')
	ntmp = roll
	roll = 0

    screen.blit(help_middle, (0,(resolution[3])+135))

    label4 = myfont.render("0 GAMES AVAILABLE", 1, (63,63,63))
    label4pos = label4.get_rect()
    label4pos.centerx = background.get_rect().centerx
    label4pos.centery = (resolution[3])+163
    screen.blit(label4, label4pos)

#    help_down = pygame.Surface((resolution[0],100), pygame.SRCALPHA)
#    help_down.fill((255,255,255,128))                         # notice the alpha value in the color
#    screen.blit(help_down, (0,resolution[1]-100))

    # LEFT
    emulator_list[emulator_selection[0][0]].set_position((x,(resolution[3])-(emulator_list[emulator_selection[0][0]].get_height(1)/2)))
    emulator_list[emulator_selection[0][0]].draw(screen,1)
    # CENTER (SELECTED)
    emulator_list[emulator_selection[1][0]].set_position((x+(resolution[2])-(emulator_list[emulator_selection[1][0]].get_width(0)/2),(resolution[3])-(emulator_list[emulator_selection[1][0]].get_height()/2)))
    emulator_list[emulator_selection[1][0]].draw(screen,0)
    # RIGHT
    emulator_list[emulator_selection[2][0]].set_position((x+resolution[0]-emulator_list[emulator_selection[2][0]].get_width(1),(resolution[3])-(emulator_list[emulator_selection[2][0]].get_height(1)/2)))
    emulator_list[emulator_selection[2][0]].draw(screen,1)

# TEST
    label1 = myfont.render("X: "+str(emulator_list[0].get_position()), 1, (255,63,63))
    label2 = myfont.render("A: "+str(aceleracion), 1, (255,63,63))
    label3 = myfont.render("Res: "+str((resolution[0],resolution[1])), 1, (255,63,63))
    screen.blit(label3, (100, 50))
    screen.blit(label1, (100, 100))
    screen.blit(label2, (100, 150))
#    AAfilledRoundedRect(screen,((resolution[2])-150,800,300,60),(63,63,63),1)

    pygame.display.flip()
