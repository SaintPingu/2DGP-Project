from tools import *
from object import *

img_background : Image

import gmap
import sprite
import gui




def init():
    import tank, shell
    global img_background
    
    img_background = load_image_path('background.png')
    img_gui_control = load_image_path('gui_control.png')

    read_mapfile(1)
    gmap.init()
    tank.init()
    shell.init()
    sprite.init()

    gui.add_gui(gui.GUI(img_gui_control, (SCREEN_WIDTH//2, img_gui_control.h//2), is_transparent=False))

def draw_scene():
    update_objects()
    sprite.update_animations()
    #gui.update_gui()

    gmap.draw_map()
    gui.draw_gui()
    draw_objects()
    sprite.draw_animations()
    gmap.draw_debugs()
    
    update_canvas()