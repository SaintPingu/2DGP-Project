from tools import *
import gmap

class GUI:
    def __init__(self, image : Image, position=(0,0), theta=0, is_draw=True, flip='', is_fixed=False):
        self.image = image
        self.position = position
        self.theta = 0
        self.is_draw = is_draw
        self.is_composite = is_draw
        self.flip = flip
        self.is_fixed = is_fixed
    
    def release(self, is_delete_image=True, is_invalidate=False):
        if is_delete_image and self.image:
            del self.image

    def draw(self):
        if self.is_draw:
            self.image.composite_draw(self.theta, self.flip, *self.position)

    def invalidatae(self):
        gmap.set_invalidate_rect(self.position, self.image.w, self.image.h, grid_size=0)

    def update(self):
        if self.is_fixed == False:
            self.invalidatae()

class GUI_HP(GUI):
    def __init__(self, owner):
        super().__init__(_img_hp)
        self.owner = owner
        self.max_hp = owner.hp
        self.width = _img_hp.w
        self.height = _img_hp.h
        self.position = Vector2(*self.owner.center)
        self.update()
    
    def release(self):
        super().release(False)

    def draw(self):
        self.image.draw(*self.position, self.width, self.height)
    
    def update(self):
        super().update()
        self.position.x = self.owner.center.x
        self.position.y = self.owner.get_rect().top + 10

    def resize(self, hp):
        pass

_img_hp : Image
_list_gui : list[GUI]

def enter():
    global _list_gui, _img_hp
    _list_gui = []
    _img_hp = load_image_path('hp_bar.png')
    
def exit():
    global _list_gui, _img_hp

    for gui in _list_gui:
        gui.release()
    _list_gui.clear()
    del _list_gui

    del _img_hp

def add_gui(gui : GUI):
    _list_gui.append(gui)

def del_gui(gui : GUI):
    global _list_gui
    _list_gui.remove(gui)
    del gui

def update_gui():
    for gui in _list_gui:
        gui.update()

def draw_gui():
    for gui in _list_gui:
        gui.draw()