from tools import *
import gmap
import framework
import state_lobby

TIMER_FOR_ENDING = 10
TEXT_POS_Y = 700

_ending_count = None
_game_over_font : Font = None
_font_rect : Rect = None

def enter():
    global _ending_count, _game_over_font, _font_rect
    _ending_count = 0
    _game_over_font = load_font_path('CabinSketch-Regular', 64)
    _font_rect = Rect((SCREEN_WIDTH//2, TEXT_POS_Y), SCREEN_WIDTH, 100)

def exit():
    global _game_over_font, _font_rect
    del _game_over_font
    del _font_rect

def update():
    global _ending_count, _font_rect
    gmap.draw_background(_font_rect, False)

    _ending_count += framework.frame_time
    if _ending_count > TIMER_FOR_ENDING:
        return False
    return True

def draw(winner):
    if state_lobby.crnt_map_index == 0:
        rgb = (255, 255, 255)
    elif state_lobby.crnt_map_index == 1:
        rgb = (255, 255, 0)
    elif state_lobby.crnt_map_index == 2:
        rgb = (0, 167, 255)
    else:
        assert(0)

    if winner == 0: # player win
        if _ending_count > 1:
            _game_over_font.draw(100, TEXT_POS_Y, "Winner!", rgb)
        if _ending_count > 2:
            _game_over_font.draw(400, TEXT_POS_Y, "Winner!", rgb)
        if _ending_count > 3:
            _game_over_font.draw(700, TEXT_POS_Y, "Chicken!", rgb)
        if _ending_count > 4:
            _game_over_font.draw(1000, TEXT_POS_Y, "Dinner!", rgb)
    elif winner == -1: # ai win
        if _ending_count > 1:
            _game_over_font.draw(450, TEXT_POS_Y, "You", rgb)
        if _ending_count > 2:
            _game_over_font.draw(600, TEXT_POS_Y, "Lose", rgb)
        if _ending_count > 3:
            _game_over_font.draw(750, TEXT_POS_Y, "...", rgb)
        if _ending_count > 4:
            _game_over_font.draw(795, TEXT_POS_Y, "...", rgb)
    else:
        assert(0)