from pico2d import *
import mytool

screenWidth = 1280
screenHeight = 800

img_background : pico2d.Image
img_ground : pico2d.Image

import map
import tank

def init():
    global img_background, img_ground
    open_canvas(screenWidth, screenHeight, sync=True)
    img_background = mytool.load_image_path('background.png')
    img_ground = mytool.load_image_path('ground.png')
    img_background.draw(screenWidth//2, screenHeight//2, screenWidth, screenHeight)

    map.init()
    map.read_mapfile(1)
    map.draw_map(True)

def draw_scene():
    tank.update()