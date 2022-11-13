from tools import *
import gmap
import framework

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
    gmap.set_invalidate_rect(*_font_rect.__getitem__(), grid_size=0)

    _ending_count += framework.frame_time
    if _ending_count > TIMER_FOR_ENDING:
        return False
    return True

def draw(winner):
    if winner == 0: # player win
        if _ending_count > 1:
            _game_over_font.draw(100, TEXT_POS_Y, "Winner!", (255, 0, 0))
        if _ending_count > 2:
            _game_over_font.draw(400, TEXT_POS_Y, "Winner!", (255, 0, 0))
        if _ending_count > 3:
            _game_over_font.draw(700, TEXT_POS_Y, "Chicken!", (255, 0, 0))
        if _ending_count > 4:
            _game_over_font.draw(1000, TEXT_POS_Y, "Dinner!", (255, 0, 0))
    elif winner == -1: # ai win
        if _ending_count > 1:
            _game_over_font.draw(450, TEXT_POS_Y, "You", (255, 0, 0))
        if _ending_count > 2:
            _game_over_font.draw(600, TEXT_POS_Y, "Lose", (255, 0, 0))
        if _ending_count > 3:
            _game_over_font.draw(750, TEXT_POS_Y, "...", (255, 0, 0))
        if _ending_count > 4:
            _game_over_font.draw(800, TEXT_POS_Y, "...", (255, 0, 0))
    else:
        assert(0)