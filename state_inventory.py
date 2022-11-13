if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_battle
import tank
from gui import GUI, add_gui, del_gui

_NUM_OF_SLOT = 4

_table_weapon : dict

_gui_inventory : GUI
_rect_slots = list[Rect]

def enter():
    image_inventory = load_image_path('inventory_weapon.png')
    global _gui_inventory
    _gui_inventory = GUI(image_inventory, (555, 140), is_fixed=True)
    
    add_gui(_gui_inventory, 1)

    global _rect_slots
    _rect_slots = []
    slot_width = 34
    slot_height = 34
    slot_interval = slot_width + 2
    for i in range(_NUM_OF_SLOT):
        rect = Rect((410 + (i * slot_interval), 140), slot_width, slot_height)
        _rect_slots.append(rect)

    global _table_weapon
    _table_weapon = {
    0 : "AP",
    1 : "HP",
    2 : "MUL",
    3 : "NUCLEAR",
}

def exit():
    global _gui_inventory
    del_gui(_gui_inventory)

    global _rect_slots
    for rect in _rect_slots:
        del rect
    del _rect_slots

    global _table_weapon
    del _table_weapon

def update():
    state_battle.update()

    import gmap
    for rect in _rect_slots:
        gmap.draw_debug_rect(rect)

def draw():
    state_battle.draw()

def handle_events():
    from gui import gui_weapon

    events = get_events()
    event : Event

    for event in events:
        if event.type == SDL_MOUSEBUTTONDOWN:
            point = convert_pico2d(event.x, event.y)
            if event.button == SDL_BUTTON_LEFT:
                for idx, rect in enumerate(_rect_slots):
                    if point_in_rect(point, rect):
                        shell_name = _table_weapon[idx]

                        tank.set_shell(shell_name)
                        gui_weapon.set_image(shell_name)
                        framework.pop_state()
                        return



    state_battle.handle_events(events)


def pause():
    pass
def resume():
    pass