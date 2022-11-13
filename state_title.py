if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_lobby

image : Image
font : Font
font_show_count = 0
title_music : Music = None

def enter():
    global image, font
    image = load_image_path('title.png')
    font = load_font_path("Lemon-Regular", 64)

    global font_show_count
    font_show_count = 0

    play_bgm()


def exit():
    global image, font
    del image
    del font

def play_bgm():
    global title_music
    if title_music == None:
        title_music = load_music_path("bgm_title")
        title_music.repeat_play()

def stop_bgm():
    global title_music
    title_music.stop()
    del title_music
    title_music = None

def update():
    global font_show_count
    font_show_count = (font_show_count + framework.frame_time) % 1

def draw():
    clear_canvas()
    image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)

    if font_show_count <= 0.5:
        font.draw(250, 300, "Press Any Key To Start!", (0, 79, 212))

    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                framework.quit()
                return
            framework.change_state(state_lobby)


def pause():
    pass
def resume():
    pass