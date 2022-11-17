if __name__ == "__main__":
    quit()

from tools import *
import gmap
import framework

class GUI:
    def __init__(self, image : Image, position=(0,0), theta=0, is_draw=True, flip='', is_fixed=False, scale=1):
        self.image = image
        self.position = position
        self.theta = theta
        self.is_draw = is_draw
        self.is_composite = is_draw
        self.flip = flip
        self.is_fixed = is_fixed
        self.scale = scale
    
    def release(self):
        self.invalidate()
        del self.image

    def draw(self):
        if self.is_draw:
            self.image.composite_draw(self.theta, self.flip, *self.position, self.image.w * self.scale, self.image.h * self.scale)

    def invalidate(self):
        gmap.set_invalidate_rect(self.position, self.image.w, self.image.h, grid_size=0)

    def update(self):
        if self.is_fixed == False:
            self.invalidate()
        
    def get_rect(self):
        return Rect(self.position, self.image.w * self.scale, self.image.h * self.scale)

class GUI_HP(GUI):
    image : Image = None

    def __init__(self, owner):
        if GUI_HP.image == None:
            GUI_HP.image = load_image_path('hp_bar.png')

        super().__init__(GUI_HP.image)
        self.owner = owner
        self.max_hp = owner.hp
        self.max_width = GUI_HP.image.w
        self.width = GUI_HP.image.w
        self.height = GUI_HP.image.h
        self.position = self.owner.center[0], self.owner.center[1]

    def release(self):
        pass

    def draw(self):
        if self.is_draw:
            self.image.draw(*self.position, self.width, self.height)
    
    def update(self):
        if self.is_draw:
            self.invalidate()
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
    
    def release(self):
        pass

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
            self.invalidate()
            self.y_floating = 0
            self.is_positive_y = True
        else:
            self.update()

class GUI_Fuel(GUI):
    image : Image = None
    PIVOT = Vector2(200, 25)

    def __init__(self, owner, max_fuel):
        if GUI_Fuel.image == None:
            GUI_Fuel.image = load_image_path('fuel_hand.png')
        super().__init__(GUI_Fuel.image)
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
        self.position = (815, 52)

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
        self.image_gauge = load_image_path('gui_gauge.png')
        image_gauge_box = load_image_path('gui_gauge_box.png')
        super().__init__(image_gauge_box)

        self.position = (1115, 55)
        self.t = 0
        self.is_fill = False
    
    def update(self):
        super().update()
        if self.is_fill and self.t < 1:
            self.t += 0.5 * framework.frame_time

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

        width = int(self.image_gauge.w * self.t) 
        gauge_position = Vector2()
        gauge_position.x = int((self.position[0] - self.image_gauge.w/ 2) + width/2)
        gauge_position.y = self.position[1]

        self.image_gauge.clip_draw(0, 0, width, self.image_gauge.h, *gauge_position)


class GUI_Weapon(GUI):
    name_table = {
        "AP" : "Armour-Piercing",
        "HP" : "High-Explosive",
        "MUL" : "Multiple",
        "NUCLEAR" : "Nuclear",
    }
    def __init__(self):
        import shell
        super().__init__(shell.get_shell_image(shell.DEFAULT_SHELL), (444, 30), math.radians(90), is_fixed=True, scale=1.4)
        self.is_draw = False
        self.font = load_font_path("PermanentMarker", 20)
        self.str = ''

    def draw(self):
        super().draw()
        self.font.draw(self.position[0] + 50, self.position[1], self.str, (255,255,255))

    def set_image(self, shell_name):
        import shell
        self.is_draw = True
        self.image = shell.get_shell_image(shell_name)
        self.str = GUI_Weapon.name_table[shell_name]

    

_list_gui : list[GUI, int]
gui_weapon : GUI

rect_gui : Rect
rect_weapon : Rect
rect_item : Rect

_is_hide_gui : bool

def enter():
    global _list_gui
    _list_gui = [[],[]]

    global _is_hide_gui
    _is_hide_gui = False

    img_gui_control = load_image_path('gui_control.png')
    main_gui = GUI(img_gui_control, (SCREEN_WIDTH//2, img_gui_control.h//2), is_fixed=True)
    add_gui(main_gui, 0)
    set_debug_mode(False)

    global rect_gui, rect_weapon, rect_item
    rect_gui = Rect(main_gui.position, img_gui_control.w, img_gui_control.h)
    rect_weapon = Rect((550, 80), 258, 40)
    rect_item = Rect((345, 52), 137, 96)

    global gui_weapon
    gui_weapon = GUI_Weapon()
    add_gui(gui_weapon, 1)
    
def exit():
    global _list_gui

    for gui in all_gui():
        gui.release()
        del gui
    for layer in _list_gui:
        layer.clear()
    del _list_gui

    del GUI_HP.image
    del GUI_Fuel.image
    GUI_HP.image = None
    GUI_Fuel.image = None

    global rect_gui, rect_weapon
    del rect_gui
    del rect_weapon

def update():
    for gui in all_gui():
        gui.update()

def draw():
    if _is_hide_gui:
        return
        
    for gui in all_gui():
        gui.draw()

def add_gui(gui : GUI, depth):
    _list_gui[depth].append(gui)

def del_gui(gui : GUI):
    global _list_gui
    if _list_gui:
        for layer in _list_gui:
            if gui in layer:
                layer.remove(gui)
                gui.release()
                del gui
                return

def toggle_gui():
    global _is_hide_gui
    _is_hide_gui = not _is_hide_gui

def all_gui():
    for layer in _list_gui:
        for gui in layer:
            yield gui