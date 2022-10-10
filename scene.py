from tools import *
from object import *
import map
import sprite
import gui

screenWidth = 1280
screenHeight = 800

img_map : Image
img_background : Image
img_ground : Image
img_main_gui : Image

min_height = 0

def init():
    import shell, tank, sprite
    global img_background, img_map, img_ground
    global min_height
    
    open_canvas(screenWidth, screenHeight, sync=True)
    img_background = load_image_path('background.png')
    img_map = load_image_path('map_1.png')
    img_ground = load_image_path('ground.png')
    img_main_gui = load_image_path('gui.png')
    min_height = img_main_gui.h
    #img_background.draw(screenWidth//2, screenHeight//2)    # Empty background
    img_map.draw(screenWidth//2, screenHeight//2 + min_height//2)
    img_main_gui.draw(screenWidth//2, img_main_gui.h//2)

    map.init()
    map.read_mapfile(1)
    tank.init()
    shell.init()
    sprite.init()

def draw_scene():
    update_objects()
    sprite.update_animations()

    map.draw_map()

    draw_objects()
    sprite.draw_animations()
    update_canvas()