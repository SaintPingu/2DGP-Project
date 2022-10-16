from tools import *
import gmap

class GUI:
    def __init__(self, image : Image, position=(0,0), theta=0, is_draw=True, flip='', is_transparent=True):
        self.image = image
        self.position = position
        self.theta = 0
        self.is_draw = is_draw
        self.is_composite = is_draw
        self.flip = flip
        self.is_transparent = is_transparent

    def draw(self):
        if self.is_draw:
            self.image.composite_draw(self.theta, self.flip, *self.position)

    def update(self):
        if self.is_transparent:
            gmap.set_invalidate_rect(self.position, self.image.w, self.image.h, grid_size=0)


_list_gui : list[GUI] = []

def add_gui(gui : GUI):
    _list_gui.append(gui)

def del_gui(gui : GUI):
    _list_gui.remove(gui)
    del gui

def update_gui():
    for gui in _list_gui:
        gui.update()

def draw_gui():
    for gui in _list_gui:
        gui.draw()