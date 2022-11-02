from tools import *
import framework
import state_title
import state_battle

_image = None

def enter():
    global _image
    _image = load_image_path('lobby.png')

def exit():
    global _image
    del _image

def update():
    pass

def draw():
    clear_canvas()
    _image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    update_canvas()


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                framework.change_state(state_title)
            else:
                framework.change_state(state_battle)
            break

