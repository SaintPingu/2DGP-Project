from tools import *
import framework
import state_title

import object
import gui
import gmap
import tank
import shell
import sprite
import environment as env


def enter():
    img_gui_control = load_image_path('gui_control.png')

    object.enter()
    gui.enter()
    gmap.enter()
    read_mapfile(1)
    tank.enter()
    shell.enter()
    sprite.enter()
    env.enter()

    gui.add_gui(gui.GUI(img_gui_control, (SCREEN_WIDTH//2, img_gui_control.h//2), is_transparent=False))

def exit():
    env.exit()
    sprite.exit()
    shell.exit()
    tank.exit()
    gmap.exit()
    gui.exit()
    object.exit()

def update():
    object.update_objects()
    sprite.update_animations()
    gui.update_gui()

def draw():
    gmap.draw_map()
    gui.draw_gui()
    object.draw_objects()
    sprite.draw_animations()
    gmap.draw_debugs()
    
    update_canvas()

def handle_events():
    events = get_events()
    event : Event

    if gmap.is_draw_mode == True:
        gmap.handle_events(events)
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

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                tank.stop_tank()
            elif event.key == SDLK_LEFT:
                tank.stop_tank()

        elif event.type == SDL_MOUSEMOTION:
            mouse_pos = convert_pico2d(event.x, event.y)
            tank.send_mouse_pos(*mouse_pos)

        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                tank.fire()