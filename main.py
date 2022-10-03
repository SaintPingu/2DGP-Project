import os
from pico2d import *
import scene
import map

os.chdir(os.path.dirname(__file__))
scene.init()

running = True
while running:
    scene.draw_scene()

    events = get_events()
    event : Event

    if map.is_draw_mode == True:
        map.modify_map(events)
        continue

    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                map.start_draw_mode()
    

close_canvas()