import os
from tools import *
import scene
import gmap
import tank

os.chdir(os.path.dirname(__file__))

open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT, sync=True)
scene.init()

running = True
while running:
    scene.draw_scene()

    events = get_events()
    event : Event

    if gmap.is_draw_mode == True:
        gmap.modify_map(events)
        continue

    for event in events:
        if event.type == SDL_QUIT:
            running = False
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
    

close_canvas()