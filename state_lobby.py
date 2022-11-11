from tools import *
import framework
import state_title
import state_battle

_image = None
_image_pvp = None
_image_pve = None
_image_check = None

_position_icon_pvp = (980, 750)
_position_icon_pve = (980, 620)
_rect_pvp = None
_rect_pve = None

_crnt_mode = "PVP"
_check_position_pvp = (_position_icon_pvp[0] - 95, _position_icon_pvp[1])
_check_position_pve = (_position_icon_pve[0] - 95, _position_icon_pve[1])

_image_maps : list = None
_crnt_map_index = 0
_position_map = (520, 470)

def enter():
    global _image, _image_pvp, _image_pve, _image_check
    _image = load_image_path('lobby.png')
    _image_pvp = load_image_path('lobby_icon_pvp.png')
    _image_pve = load_image_path('lobby_icon_pve.png')
    _image_check = load_image_path('lobby_icon_check.png')

    global _image_maps
    _image_maps = []
    _image_maps.append(load_image_path("map_1.png"))

    global _rect_pvp, _rect_pve
    _rect_pvp = Rect(_position_icon_pvp, _image_pvp.w,  _image_pvp.h)
    _rect_pve = Rect(_position_icon_pve, _image_pve.w,  _image_pve.h)

    global _crnt_mode
    _crnt_mode = "PVP"

def exit():
    global _image, _image_pvp, _image_pve, _image_check, _rect_pvp, _rect_pve
    del _image
    del _image_pvp
    del _image_pve
    del _image_check
    del _rect_pvp
    del _rect_pve

def update():
    pass

def draw():
    clear_canvas()
    _image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    _image_pvp.draw(*_position_icon_pvp)
    _image_pve.draw(*_position_icon_pve)
    if _crnt_mode == "PVP":
        _image_check.draw(*_check_position_pvp)
    else:
        _image_check.draw(*_check_position_pve)
    
    _image_maps[_crnt_map_index].draw(*_position_map, 520, 500)
    update_canvas()


def handle_events():
    global _crnt_mode
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
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                point = convert_pico2d(event.x, event.y)
                if(point_in_rect(point, _rect_pvp)):
                    _crnt_mode = "PVP"
                elif(point_in_rect(point, _rect_pve)):
                    _crnt_mode = "PVE"

def get_mode():
    return _crnt_mode