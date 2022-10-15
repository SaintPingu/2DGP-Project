from tools import *
from object import *

img_background : Image
img_ground : Image
img_main_gui : Image

import gmap
import sprite
import gui




def init():
    import tank, shell
    global img_background, img_ground, img_main_gui
    
    img_background = load_image_path('background.png')
    img_ground = load_image_path('ground.png')
    img_main_gui = load_image_path('gui.png')
    img_main_gui.draw(SCREEN_WIDTH//2, img_main_gui.h//2)

    read_mapfile(1)
    gmap.init()
    tank.init()
    shell.init()
    sprite.init()

def draw_scene():
    update_objects()
    sprite.update_animations()

    gmap.draw_map()
    draw_objects()
    sprite.draw_animations()
    gmap.draw_debugs()
    
    img_main_gui.draw(SCREEN_WIDTH//2, img_main_gui.h//2)
    update_canvas()