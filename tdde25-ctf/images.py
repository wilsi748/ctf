import pygame
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]

#
# Load an image from the data directory
#
def load_image(file):
    "loads an image, prepares it for play"
    file = os.path.join(main_dir, 'data', file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit('Could not load image "%s" %s'%(file, pygame.get_error()))
    return surface.convert_alpha()

#
# Load a sound from the data directory
#
def load_sound(file):
    file = os.path.join(main_dir, 'data', file)
    return file

# Define the default size of tiles
TILE_SIZE = 40

# Image of an explosion
explosion = load_image('explosion.png')

# Image of a grass tile
grass     = load_image('grass.png')

# Image of a rock box (wall)
rockbox   = load_image('rockbox.png')

# Image of a metal box
metalbox  = load_image('metalbox.png')

# Image of a wood box
woodbox   = load_image('woodbox.png')

# Image of flag
flag      = load_image('flag.png')

# Image of bullet
bullet    = load_image('missile.png')

# List of image of tanks of different colors
tanks     = [load_image('tank_orange.png'), load_image('tank_blue.png'), load_image('tank_white.png'),
             load_image('tank_yellow.png'), load_image('tank_red.png'),  load_image('tank_gray.png')]

# List of image of bases corresponding to the color of each tank
bases     = [load_image('base_orange.png'), load_image('base_blue.png'), load_image('base_white.png'),
             load_image('base_yellow.png'), load_image('base_red.png'),  load_image('base_gray.png')]
