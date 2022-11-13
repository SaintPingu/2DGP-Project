from tools import *
import gmap
import framework

_ending_count = None
_game_over_font : Font = None
_font_rect : Rect = None

def enter():
    global _ending_count, _game_over_font, _font_rect
    _ending_count = 0
    _game_over_font = load_font_path('CabinSketch-Regular', 64)
    _font_rect = Rect((SCREEN_WIDTH//2, 800), SCREEN_WIDTH, 100)

def exit():
    global _game_over_font, _font_rect
    del _game_over_font
    del _font_rect

def update():
    global _ending_count
    gmap.draw_background(_font_rect, False)
    _ending_count += framework.frame_time
    if _ending_count > 5:
        return False
    return True

def draw(winner):
    if winner == 0: # player win
        if _ending_count > 1:
            _game_over_font.draw(100, 800, "Winner!", (255, 0, 0))
        if _ending_count > 2:
            _game_over_font.draw(400, 800, "Winner!", (255, 0, 0))
        if _ending_count > 3:
            _game_over_font.draw(700, 800, "Chicken!", (255, 0, 0))
        if _ending_count > 4:
            _game_over_font.draw(1000, 800, "Dinner!", (255, 0, 0))
    elif winner == -1: # ai win
        if _ending_count > 1:
            _game_over_font.draw(450, 800, "You", (255, 0, 0))
        if _ending_count > 2:
            _game_over_font.draw(600, 800, "Lose", (255, 0, 0))
        if _ending_count > 3:
            _game_over_font.draw(750, 800, "...", (255, 0, 0))
        if _ending_count > 4:
            _game_over_font.draw(800, 800, "...", (255, 0, 0))
    else:
        assert(0)