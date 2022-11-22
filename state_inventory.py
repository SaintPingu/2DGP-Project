if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_battle


class Inventory:
    def __init__(self, image : Image, position : tuple, table : dict[int, str], slot_position : tuple):
        from gui import GUI, add_gui
        self.gui = GUI(image, position, is_fixed=True)
        self.rect = self.gui.get_rect()
        self.table = table
        add_gui(self.gui, 1)

        self.slots = []
        slot_width = 34
        slot_height = 34
        slot_interval = slot_width + 2
        for i in range(len(table)):
            rect = Rect((slot_position[0] + (i * slot_interval), slot_position[1]), slot_width, slot_height)
            self.slots.append(rect)
    
    def exit(self):
        from gui import del_gui
        del_gui(self.gui)
        del self.rect

        for rect in self.slots:
            del rect
        del self.slots

    def select(self, index):
        pass


class Inven_Weapon(Inventory):
    def __init__(self):
        image = load_image_path('inventory_weapon.png')
        position = (555, 140)
        table = {
            0 : "AP",
            1 : "HP",
            2 : "MUL",
            3 : "NUCLEAR",
            4 : "HOMING"
        }
        super().__init__(image, position, table, (555 - 145, 140))

    def select(self, index):
        import tank
        from gui import gui_weapon
        shell_name = self.table[index]

        tank.set_shell(shell_name)
        gui_weapon.set_image(shell_name)

class Inven_Item(Inventory):
    def __init__(self):
        image = load_image_path('inventory_items.png')
        position = (345, 140)
        self.image_double = load_image_path('item_double.png')
        self.image_extension = load_image_path('item_extension.png')
        self.image_teleport = load_image_path('shell_teleport.png')
        self.image_heal = load_image_path('item_heal.png')
        table = {
            0 : ( "double", self.image_double ),
            1 : ( "extension", self.image_extension ),
            2 : ( "TP", self.image_teleport ),
            3 : ( "heal", self.image_heal ),
        }
        super().__init__(image, position, table, (345 - 145, 140))

    def exit(self):
        del self.image_double
        del self.image_extension
        del self.image_heal
        super().exit()

    def select(self, index):
        import tank
        tank.set_item(self.table[index])

_inventory_name : str
inventory : Inventory
_table_inventory : dict[str, Inventory]= {
    "weapon" : Inven_Weapon,
    "item" : Inven_Item,
}

def set_window(name : str):
    global _inventory_name
    _inventory_name = name

def get_window():
    return _inventory_name

def enter():
    assert(_inventory_name in _table_inventory.keys())

    global inventory
    inventory = _table_inventory[_inventory_name]()

def exit():
    global inventory
    inventory.exit()

def update():
    state_battle.update()

def draw():
    state_battle.draw()

def handle_events():
    global inventory

    events = get_events()
    event : Event

    for event in events:
        if event.type == SDL_MOUSEBUTTONDOWN:
            point = convert_pico2d(event.x, event.y)
            if event.button == SDL_BUTTON_LEFT:
                if point_in_rect(point, inventory.rect):
                    for idx, rect in enumerate(inventory.slots):
                        if point_in_rect(point, rect):
                            from sound import play_sound
                            play_sound('click')
                            inventory.select(idx)
                            framework.pop_state()
                    return



    state_battle.handle_events(events)


def pause():
    pass
def resume():
    pass