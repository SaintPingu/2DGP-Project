if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_title
import state_lobby
import sound

import object
import gui
import gmap
import tank
import shell
import sprite
import ending
import environment as env

_is_game_over = False
_winner = 0

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
    sound.enter('battle')

    map_index = state_lobby.crnt_map_index + 1
    #map_index = -3
    gmap.read_mapfile(map_index, mode)
    sound.play_battle_bgm(map_index)

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
    sound.del_sounds()


def update():
    global _is_game_over, _winner

    object.update()
    sprite.update()
    gui.update()
    _winner = tank.update()
    if _winner <= 0:
        if _is_game_over == False:
            if _winner == 0:
                sound.play_bgm('win')
            elif _winner == -1:
                sound.play_bgm('lose')
            else:
                assert(0)

        _is_game_over = True

    if _is_game_over:
        if ending.update() == False:
            framework.change_state(state_title)

def draw():

    gmap.draw()
    gui.draw()
    object.draw()
    sprite.draw()
    gmap.draw_debugs()

    if _is_game_over:
        ending.draw(_winner)
    
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
            return

        tank.handle_event(event)

        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                gmap.start_draw_mode()

def pause():
    pass
def resume():
    pass