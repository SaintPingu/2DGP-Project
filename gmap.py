if __name__ == "__main__":
    quit()

from tools import *
from object import *
import scene
import tank

img_map : Image
img_debug : Image
img_debug_air : Image

DEFAULT_DRAW_RADIUS = 3
radius_draw = DEFAULT_DRAW_RADIUS
is_draw_mode = False
is_create_block = False
is_delete_block = False
is_print_mouse_pos = False

rect_inv_list : list[Rect] = []
rect_debug_list : list[Rect] = []

tank_obj = None


def init():
    global img_debug, img_debug_air
    img_debug = load_image_path('debug.png')
    img_debug_air = load_image_path('debug_air.png')


##### DRAW ######
def modify_map(events : list):
    global is_draw_mode
    global is_create_block, is_delete_block, is_print_mouse_pos
    global radius_draw
    global tank_obj
    global DEBUG

    if is_draw_mode == False:
        return
    
    event : Event
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == None:
                continue
            elif SDLK_1 <= event.key <= SDLK_9:
                radius_draw = event.key - SDLK_0
            elif event.key == SDLK_KP_MULTIPLY:
                radius_draw *= 2
            elif event.key == SDLK_KP_DIVIDE:
                radius_draw //= 2
            elif event.key == SDLK_F1:
                stop_draw_mode()
                return
            elif event.key == SDLK_F2:
                DEBUG = not DEBUG
                return
            elif event.key == SDLK_F5:
                save_mapfile()
            elif event.key == SDLK_F6:
                draw_map(True)
            elif event.key == SDLK_F9:
                if tank_obj == None:
                    tank_obj = tank.Tank()
                    add_object(tank_obj)
                else:
                    set_invalidate_rect(*tank_obj.get_rect().__getitem__())
                    delete_object(tank_obj)
                    tank_obj = None
            elif event.key == SDLK_F10:
                is_print_mouse_pos = not is_print_mouse_pos
            continue
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                if tank_obj:
                    tank_obj.create()
                    return
                is_create_block = True
            elif event.button == SDL_BUTTON_RIGHT:
                is_delete_block = True
        elif event.type == SDL_MOUSEBUTTONUP:
            is_create_block = False
            is_delete_block = False
            continue

        mouse_pos = (-1, -1)
        if event.x != None:
            mouse_pos = convert_pico2d(event.x, event.y)

        if mouse_pos[0] < 0:
            continue
        if tank_obj and not tank_obj.is_created:
            tank_obj.set_pos(mouse_pos)
        elif is_create_block:
            create_block(radius_draw, mouse_pos)
        elif is_delete_block:
            delete_block(radius_draw, mouse_pos)
        
        if is_print_mouse_pos:
            print(mouse_pos)
    
def start_draw_mode():
    global is_draw_mode
    is_draw_mode = True

def stop_draw_mode():
    global is_draw_mode, radius_draw
    radius_draw = DEFAULT_DRAW_RADIUS
    is_draw_mode = False

def draw_map(is_draw_full=False):
    global rect_inv_list

    if is_draw_full:
        rect_inv_list.clear()
        rect_inv_list.append(Rect((SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + scene.MIN_HEIGHT//2), SCREEN_WIDTH, SCREEN_HEIGHT - scene.MIN_HEIGHT))
    elif len(rect_inv_list) == 0:
        return

    # draw background
    for rect_inv in rect_inv_list:
        scene.img_background.clip_draw(int(rect_inv.origin[0]), int(rect_inv.origin[1] - scene.MIN_HEIGHT), int(rect_inv.width), int(rect_inv.height), *rect_inv.get_fCenter())
        if DEBUG:
            draw_rectangle(rect_inv.origin[0], rect_inv.origin[1], rect_inv.origin[0] + int(rect_inv.width), rect_inv.origin[1] + int(rect_inv.height))

    # draw grounds
    block_counts = []
    for rect_inv in rect_inv_list:
        block_count = 0        
        cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)

        for cell_y in range(cell_start_y, cell_end_y + 1):
            for cell_x in range(cell_start_x, cell_end_x + 1):
                if out_of_range(cell_x, cell_y, X_CELL_COUNT, Y_CELL_COUNT):
                    continue
                block_type = get_block(cell_x, cell_y)
                if block_type == BLOCK_NONE:
                    continue

                posX, posY = get_pos_from_cell(cell_x, cell_y)
                originX, originY = get_origin_from_cell(cell_x, cell_y)

                if block_type == BLOCK_GROUND:
                    scene.img_ground.clip_draw(originX, originY, CELL_SIZE, CELL_SIZE, posX, posY)
                    set_block(cell_x, cell_y, -BLOCK_GROUND)
                    block_count += 1

                elif block_type == BLOCK_DEBUG:
                    img_debug.draw(posX, posY, CELL_SIZE, CELL_SIZE)

                elif block_type == BLOCK_DEBUG_AIR:
                    img_debug_air.draw(posX, posY, CELL_SIZE, CELL_SIZE)

                else:
                    continue
        
        block_counts.append(block_count)

    for idx, rect_inv in enumerate(rect_inv_list):
        cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)
        block_count = block_counts[idx]

        is_end = False
        for cell_y in range(cell_start_y, cell_end_y + 1):
            for cell_x in range(cell_start_x, cell_end_x + 1):
                if block_count <= 0:
                    is_end = True
                    break
                elif out_of_range(cell_x, cell_y, X_CELL_COUNT, Y_CELL_COUNT):
                    continue
                block = get_block(cell_x, cell_y)
                if block < 0:
                    set_block(cell_x, cell_y, -block)
                    block_count -= 1
            if is_end:
                break

    if len(rect_debug_list) > 0:
        for rect in rect_debug_list:
            draw_rectangle(rect.origin[0], rect.origin[1], rect.origin[0] + rect.width, rect.origin[1]+rect.height)
        rect_debug_list.clear()

    rect_inv_list.clear()



##### BLOCK #####
def create_block(radius, mouse_pos):
    draw_block(radius, mouse_pos, BLOCK_GROUND)

def delete_block(radius, mouse_pos):
    draw_block(radius, mouse_pos, BLOCK_NONE)

def draw_block(radius, position, block_type):
    col, row = get_cell(position)
    x = -radius

    COLL_VAL = 0.5
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            cell_x = col+x
            cell_y = row+y
            if out_of_range(cell_x, cell_y, X_CELL_COUNT, Y_CELL_COUNT):
                continue
            elif row + y < scene.MIN_HEIGHT // CELL_SIZE:
                continue
            cell_pos = get_pos_from_cell(cell_x, cell_y)
            distance = (Vector2(*position) - Vector2(*cell_pos)).get_norm()
            if distance <= radius * CELL_SIZE + COLL_VAL:
                set_block(col + x, row + y, block_type)

    add_invalidate(position, radius*2 * CELL_SIZE, radius*2 * CELL_SIZE)




##### Invalidate #####
# BUG : Distortion background when move tank
def set_invalidate_rect(center, width=0, height=0, scale=1, square=False):
    CORR_VAL = 2

    width *= scale
    height *= scale
    width += CORR_VAL
    height += CORR_VAL

    if square:
        if width > height:
            height = width
        else:
            width = height
    
    add_invalidate(center, width, height)

def add_invalidate(center, width, height):
    global rect_inv_list

    rect_inv = Rect.get_rect_int(Rect(center, width, height))

    if rect_inv.left < 0:
        rect_inv.set_origin((0, rect_inv.bottom), rect_inv.right, rect_inv.height)
    elif rect_inv.right > SCREEN_WIDTH:
        rect_inv.set_origin((rect_inv.left, rect_inv.bottom), SCREEN_WIDTH - rect_inv.left, rect_inv.height)

    if rect_inv.bottom <= scene.MIN_HEIGHT:
        rect_inv.set_origin((rect_inv.left, scene.MIN_HEIGHT), rect_inv.width, rect_inv.top - scene.MIN_HEIGHT + 1)
    elif rect_inv.top > SCREEN_HEIGHT:
        rect_inv.set_origin((rect_inv.left, rect_inv.bottom), rect_inv.width, SCREEN_HEIGHT - rect_inv.bottom)

    rect_inv_list.append(rect_inv)








##### DEBUG #####
def draw_debug_cell(cell):
    r = CELL_SIZE//2
    pos = get_pos_from_cell(*cell)
    rect_debug_list.append(Rect(pos, r, r))
def draw_debug_cells(cells):
    for cell in cells:
        draw_debug_cell(cell)
def draw_debug_vector(vector):
    rect_debug_list.append(Rect(vector, 1, 1))
def draw_debug_vectors(vectors):
    for vector in vectors:
        draw_debug_vector(vector)
def draw_debug_point(point):
    rect_debug_list.append(Rect(point, 2, 2))
def draw_debug_rect(rect : Rect):
    rect_debug_list.append(rect)