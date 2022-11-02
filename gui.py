from tools import *
import gmap

_img_hp : Image
_img_fuel : Image

def enter():
    global _list_gui, _img_hp, _img_fuel
    _list_gui = []
    _img_hp = load_image_path('hp_bar.png')
    _img_fuel = load_image_path('fuel_hand.png')
    
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
    for gui in _list_gui.__reversed__():
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
        self.update_gauge()
    
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
    PIVOT = Vector2(200, 25)
    def __init__(self, owner, max_fuel):
        super().__init__(_img_fuel)
        self.owner = owner
        self.max_fuel = max_fuel
        self.position = GUI_Fuel.PIVOT
        self.vector : Vector2 = None
    
    def update(self):
        super().update()
        t = self.owner.fuel / self.max_fuel
        degree = -100 + (t * 105)
        self.theta = math.radians(degree)
        self.vector = Vector2.up().get_rotated(self.theta)

        self.position = GUI_Fuel.PIVOT + (self.vector * 15)

    def draw(self):
        if self.owner and self.owner.is_turn == True:
            super().draw()
        
class GUI_LAUNCH(GUI):
    def __init__(self):
        self.image_locked = load_image_path('gui_locked.png')
        self.image_fire = load_image_path('gui_fire.png')
        super().__init__(self.image_locked)

        self.state_list = ['locked', 'fire']
        self.position = (815, 55)

        self.state_table = {
            'locked' : self.image_locked,
            'fire' : self.image_fire,
        }
        

    def release(self):
        del self.image_locked
        del self.image_fire

    def set_state(self, state):
        wrong_count = 0
        for s in self.state_list:
            if s == state:
                break
            wrong_count += 1

        if wrong_count == len(self.state_list):
            assert(0)

        self.image = self.state_table[state]

class GUI_GUAGE(GUI):
    def __init__(self):
        self.image_guage = load_image_path('gui_gauge.png')
        image_guage_box = load_image_path('gui_gauge_box.png')
        super().__init__(image_guage_box)

        self.position = (1115, 55)
        self.t = 0
        self.is_fill = False
    
    def update(self):
        super().update()
        if self.is_fill and self.t < 1:
            self.t += 0.01

    def reset(self):
        self.t = 0
    
    def fill(self, is_fill):
        self.is_fill = is_fill
    
    def set_fill(self, amount):
        self.t = amount
        self.t = clamp(0, self.t, 1)
    def get_filled(self):
        return self.t

    def draw(self):
        super().draw()

        width = int(self.image_guage.w * self.t) 
        gauge_position = Vector2()
        gauge_position.x = int((self.position[0] - self.image_guage.w/ 2) + width/2)
        gauge_position.y = self.position[1]

        self.image_guage.clip_draw(0, 0, width, self.image_guage.h, *gauge_position)

        



    

_list_gui : list[GUI]

def add_gui(gui : GUI):
    _list_gui.append(gui)

def del_gui(gui : GUI):
    global _list_gui
    if _list_gui:
        _list_gui.remove(gui)
        gui.release()