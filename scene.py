from pico2d import *
from mytool import *

screenWidth = 1280
screenHeight = 720

img_background : pico2d.Image
img_ground : pico2d.Image

import map
import tank

def init():
    global img_background, img_ground
    open_canvas(screenWidth, screenHeight, sync=True)
    img_background = load_image_path('background.png')
    img_ground = load_image_path('ground.png')
    img_background.draw(screenWidth//2, screenHeight//2, screenWidth, screenHeight)
    
    map.init()
    map.read_mapfile(0)
    map.invalidate_map()
    map.draw_map()

def draw_scene():
    tank.update()