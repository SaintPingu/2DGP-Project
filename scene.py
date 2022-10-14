from tools import *
from object import *
import gmap
import sprite
import gui

img_background : Image
img_ground : Image
img_main_gui : Image

min_height = 0

def init():
    import shell, tank, sprite
    global img_background, img_ground, img_main_gui
    global min_height
    
    img_background = load_image_path('background.png')
    img_ground = load_image_path('ground.png')
    img_main_gui = load_image_path('gui.png')
    min_height = img_main_gui.h
    img_main_gui.draw(SCREEN_WIDTH//2, img_main_gui.h//2)

    gmap.init()
    gmap.read_mapfile(1)
    tank.init()
    shell.init()
    sprite.init()

def draw_scene():
    update_objects()
    sprite.update_animations()

    gmap.draw_map()

    draw_objects()
    sprite.draw_animations()
    img_main_gui.draw(SCREEN_WIDTH//2, img_main_gui.h//2)
    update_canvas()