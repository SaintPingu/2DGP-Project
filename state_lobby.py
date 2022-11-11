from tools import *
import framework
import state_title
import state_battle

# images
_image = None
_image_pvp = None
_image_pve = None
_image_check = None
_image_arrow = None
_image_start = None

# buttons
_position_icon_pvp = (980, 750)
_position_icon_pve = (980, 620)
_button_pvp = None
_button_pve = None

_position_icon_arrow_left = (200, 450)
_position_icon_arrow_right = (200 + 630, 450)
_button_arrow_left = None
_button_arrow_right = None

_position_icon_start = (515, 125)
_button_start = None


# other icons
_crnt_mode = "PVP"
_check_position_pvp = (_position_icon_pvp[0] - 95, _position_icon_pvp[1])
_check_position_pve = (_position_icon_pve[0] - 95, _position_icon_pve[1])


# global
_image_maps : list = None
_crnt_map_index = 0
_position_map = (520, 450)

def enter():
    # icon images
    global _image, _image_pvp, _image_pve, _image_check, _image_arrow, _image_start
    _image = load_image_path('lobby.png')
    _image_pvp = load_image_path('lobby_icon_pvp.png')
    _image_pve = load_image_path('lobby_icon_pve.png')
    _image_check = load_image_path('lobby_icon_check.png')
    _image_arrow = load_image_path('lobby_icon_arrow.png')
    _image_start = load_image_path('lobby_icon_start.png')

    # map images
    global _image_maps
    _image_maps = []
    _image_maps.append(load_image_path("map_1.png"))
    _image_maps.append(load_image_path("map_2.png"))

    # set buttons
    global _button_pvp, _button_pve
    _button_pvp = Rect(_position_icon_pvp, _image_pvp.w,  _image_pvp.h)
    _button_pve = Rect(_position_icon_pve, _image_pve.w,  _image_pve.h)

    global _button_arrow_left, _button_arrow_right
    _button_arrow_left = Rect(_position_icon_arrow_left, _image_arrow.w,  _image_arrow.h)
    _button_arrow_right = Rect(_position_icon_arrow_right, _image_arrow.w,  _image_arrow.h)

    global _button_start
    _button_start = Rect(_position_icon_start, _image_start.w, _image_start.h)

    # set globals
    global _crnt_mode
    _crnt_mode = "PVP"

def exit():
    global _image, _image_pvp, _image_pve, _image_check, _image_arrow
    del _image
    del _image_pvp
    del _image_pve
    del _image_check

    global _button_pvp, _button_pve, _button_arrow_left,_button_arrow_right
    del _button_pvp
    del _button_pve
    del _button_arrow_left
    del _button_arrow_right

def update():
    pass

def draw():
    clear_canvas()
    _image.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    _image_maps[_crnt_map_index].draw(*_position_map, 520, 500)

    _image_pvp.draw(*_position_icon_pvp)
    _image_pve.draw(*_position_icon_pve)

    _image_arrow.composite_draw(0, 'h', *_position_icon_arrow_left)
    _image_arrow.draw(*_position_icon_arrow_right)

    _image_start.draw(*_position_icon_start)

    if _crnt_mode == "PVP":
        _image_check.draw(*_check_position_pvp)
    else:
        _image_check.draw(*_check_position_pve)
    
    update_canvas()


def handle_events():
    global _crnt_mode, _crnt_map_index

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                framework.change_state(state_title)
                return
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                point = convert_pico2d(event.x, event.y)
                if(point_in_rect(point, _button_pvp)):
                    _crnt_mode = "PVP"
                elif(point_in_rect(point, _button_pve)):
                    _crnt_mode = "PVE"
                elif(point_in_rect(point, _button_arrow_left)):
                    _crnt_map_index -= 1
                elif(point_in_rect(point, _button_arrow_right)):
                    _crnt_map_index += 1
                elif(point_in_rect(point, _button_start)):
                    framework.change_state(state_battle)
                    return
                _crnt_map_index = clamp(0, _crnt_map_index, len(_image_maps) - 1)

def get_mode():
    return _crnt_mode