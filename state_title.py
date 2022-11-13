if __name__ == "__main__":
    quit()

from tools import *
import framework
import state_lobby

image = None

def enter():
    global image
    image = load_image_path('title.png')

def exit():
    global image
    del image

def update():
    pass

def draw():
    clear_canvas()
    image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
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