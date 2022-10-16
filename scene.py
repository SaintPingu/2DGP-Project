from tools import *
from object import *

import gmap
import sprite
import gui
import environment as env



def init():
    import tank, shell
    
    img_gui_control = load_image_path('gui_control.png')

    gmap.init()
    read_mapfile(1)
    tank.init()
    shell.init()
    sprite.init()
    env.init()

    gui.add_gui(gui.GUI(img_gui_control, (SCREEN_WIDTH//2, img_gui_control.h//2), is_transparent=False))

def draw_scene():
    update_objects()
    sprite.update_animations()
    gui.update_gui()

    gmap.draw_map()
    gui.draw_gui()
    draw_objects()
    sprite.draw_animations()
    gmap.draw_debugs()
    
    update_canvas()