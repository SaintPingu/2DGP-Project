from tools import *
import gmap

_img_hp : Image
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
    _list_gui = None

    del _img_hp

def update():
    for gui in _list_gui:
        gui.update()

def draw():
    for gui in _list_gui:
        gui.draw()

class GUI:
    def __init__(self, image : Image, position=(0,0), theta=0, is_draw=True, flip='', is_fixed=False):
        self.image = image
        self.position = position
        self.theta = 0
        self.is_draw = is_draw
        self.is_composite = is_draw
        self.flip = flip
        self.is_fixed = is_fixed
    
    def release(self, is_delete_image=True):
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
        self.max_width = _img_hp.w
        self.width = _img_hp.w
        self.height = _img_hp.h
        self.position = self.owner.center[0], self.owner.center[1]

    def draw(self):
        if self.is_draw:
            self.image.draw(*self.position, self.width, self.height)
    
    def update(self):
        self.invalidatae()
        self.position = (self.owner.center.x, self.owner.get_rect().top + 20)
    
    def update_gauge(self):
        self.width = self.max_width * (self.owner.hp / self.max_hp)

    def resize(self, hp):
        pass

class GUI_Select_Tank(GUI):
    def __init__(self, image: Image):
        super().__init__(image)
        self.owner = None
        self.is_positive_y = True
        self.y_floating = 0
    
    def draw(self):
        if self.owner:
            super().draw()
    
    def update(self):
        if self.owner:
            MAX_FLOATING_Y = 5
            FLOATING_AMOUNT = 0.2
            if self.is_positive_y:
                self.y_floating += FLOATING_AMOUNT
                if self.y_floating >= MAX_FLOATING_Y:
                    self.is_positive_y = False
            else:
                self.y_floating -= FLOATING_AMOUNT
                if self.y_floating <= -MAX_FLOATING_Y:
                    self.is_positive_y = True

            super().update()
            self.position = (self.owner.center.x, self.owner.get_rect().top + 45 + self.y_floating)
    
    def set_owner(self, owner):
        self.owner = owner
        if self.owner is None:
            self.invalidatae()
            self.y_floating = 0
            self.is_positive_y = True
        else:
            self.update()

class GUI_Fuel(GUI):
    def __init__(self, image: Image):
        super().__init__(image)
        self.owner = None

_list_gui : list[GUI]

def add_gui(gui : GUI):
    _list_gui.append(gui)

def del_gui(gui : GUI):
    global _list_gui
    if _list_gui:
        _list_gui.remove(gui)
        gui.release()