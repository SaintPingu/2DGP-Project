if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_title
import state_lobby
import state_inventory

import object
import gui
import gmap
import tank
import shell
import sprite
import ending
import environment as env

_is_game_over = None

def enter():
    from  state_lobby import get_mode
    mode = get_mode()

    object.enter()
    gmap.enter()
    shell.enter()
    gui.enter()
    tank.enter()
    sprite.enter()
    env.enter()
    ending.enter()
    gmap.read_mapfile(state_lobby.crnt_map_index + 1, mode)

    global _is_game_over
    _is_game_over = False


def exit():
    env.exit()
    sprite.exit()
    shell.exit()
    tank.exit()
    gui.exit()
    object.exit()
    ending.exit()
    gmap.exit()


def update():
    global _is_game_over

    object.update()
    sprite.update()
    gui.update()
    if tank.update() == False:
        _is_game_over = True

    if _is_game_over:
        ending.update()

def draw():

    gmap.draw()
    gui.draw()
    object.draw()
    sprite.draw()
    gmap.draw_debugs()

    if _is_game_over:
        ending.draw()
    
    update_canvas()

def handle_events(events=None):
    if events == None:
        events = get_events()
    event : Event

    if gmap.is_draw_mode == True:
        gmap.handle_draw_mode_events(events)
        return

    for event in events:
        if event.type == SDL_QUIT:
            framework.change_state(state_title)
            
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                gmap.start_draw_mode()
            elif event.key == SDLK_RIGHT:
                tank.move_tank(RIGHT)
            elif event.key == SDLK_LEFT:
                tank.move_tank(LEFT)
            elif event.key == SDLK_5:
                tank.crnt_tank.fuel = tank.Tank.MAX_FUEL
            elif event.key == SDLK_F10:
                gui.toggle_gui()
            elif event.key == SDLK_SPACE:
                tank.fill_gauge()

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT or event.key == SDLK_LEFT:
                tank.stop_tank()
            elif event.key == SDLK_SPACE:
                tank.stop_gauge()
                if framework.state_in_stack(state_inventory):
                    framework.pop_state()

        elif event.type == SDL_MOUSEMOTION:
            mouse_pos = convert_pico2d(event.x, event.y)
            tank.send_mouse_pos(*mouse_pos)

        elif event.type == SDL_MOUSEBUTTONDOWN:
            point = convert_pico2d(event.x, event.y)
            if event.button == SDL_BUTTON_LEFT:
                if point_in_rect(point, gui.rect_gui):
                    if tank.crnt_tank != None:
                        if point_in_rect(point, gui.rect_weapon):
                            if not framework.state_in_stack(state_inventory):
                                framework.push_state(state_inventory)
                            else:
                                framework.pop_state()
                else:
                    tank.toggle_lock()

def pause():
    pass
def resume():
    pass