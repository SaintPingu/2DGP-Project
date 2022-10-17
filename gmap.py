if __name__ == "__main__":
    quit()

from tools import *
from object import *
import tank
import environment as env

img_background : Image
_img_ground : Image

DEFAULT_DRAW_RADIUS = 3
_radius_draw = DEFAULT_DRAW_RADIUS
is_draw_mode = False
_is_create_block = False
_is_delete_block = False
_is_print_mouse_pos = False

_rect_inv_list : list[InvRect] = []
_rect_debug_list : list[InvRect] = []

tank_obj : tank = None
wind : env.Wind = None

def enter():
    global wind, img_background, _img_ground
    img_background = load_image_path('background.png')
    _img_ground = load_image_path('ground.png')
    wind = env.Wind()
    wind.randomize()

    global _rect_inv_list, _rect_debug_list
    _rect_inv_list = []
    _rect_debug_list = []

def exit():
    global img_background, _img_ground
    del img_background
    del _img_ground

    global _rect_inv_list, _rect_debug_list
    for rect in _rect_inv_list:
        del rect
    for rect in _rect_debug_list:
        del rect
    _rect_inv_list.clear()
    _rect_debug_list.clear()
    del _rect_inv_list
    del _rect_debug_list

    global wind
    del wind

    global tank_obj
    tank_obj = None

##### DRAW ######
def handle_events(events : list):
    global is_draw_mode
    global _is_create_block, _is_delete_block, _is_print_mouse_pos
    global _radius_draw
    global tank_obj, wind

    if is_draw_mode == False:
        return
    
    event : Event
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == None:
                continue
            elif SDLK_1 <= event.key <= SDLK_9:
                _radius_draw = event.key - SDLK_0
            elif event.key == SDLK_KP_MULTIPLY:
                _radius_draw *= 2
            elif event.key == SDLK_KP_DIVIDE:
                _radius_draw //= 2
            elif event.key == SDLK_F1:
                stop_draw_mode()
                return
            elif event.key == SDLK_F2:
                toggle_debug_mode()
                return
            elif event.key == SDLK_F5:
                save_mapfile()
            elif event.key == SDLK_F6:
                draw_map(True)
            elif event.key == SDLK_F7:
                wind.randomize()
            elif event.key == SDLK_F9:
                if tank_obj == None:
                    tank_obj = tank.Tank()
                    add_object(tank_obj)
                else:
                    set_invalidate_rect(*tank_obj.get_rect().__getitem__())
                    delete_object(tank_obj)
                    tank_obj = None
            elif event.key == SDLK_F10:
                _is_print_mouse_pos = not _is_print_mouse_pos
            continue

        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                if tank_obj:
                    tank_obj.create()
                    return
                _is_create_block = True
            elif event.button == SDL_BUTTON_RIGHT:
                _is_delete_block = True

        elif event.type == SDL_MOUSEBUTTONUP:
            _is_create_block = False
            _is_delete_block = False
            continue

        mouse_pos = (-1, -1)
        if event.x != None:
            mouse_pos = convert_pico2d(event.x, event.y)

        if mouse_pos[0] < 0:
            continue
        if tank_obj and not tank_obj.is_created:
            tank_obj.set_pos(mouse_pos)
        elif _is_create_block:
            create_block(_radius_draw, mouse_pos)
        elif _is_delete_block:
            delete_block(_radius_draw, mouse_pos)
        
        if _is_print_mouse_pos:
            print(mouse_pos)
    
def start_draw_mode():
    global is_draw_mode
    is_draw_mode = True

def stop_draw_mode():
    global is_draw_mode, _radius_draw
    _radius_draw = DEFAULT_DRAW_RADIUS
    is_draw_mode = False

def draw_ground(rect : Rect):
    _img_ground.clip_draw(int(rect.origin[0]), int(rect.origin[1]), int(rect.width), int(rect.height), *rect.get_fCenter())
def draw_background(rect : Rect):
    img_background.clip_draw(int(rect.origin[0]), int(rect.origin[1]), int(rect.width), int(rect.height), *rect.get_fCenter())

def get_block_set(rect_inv : Rect):
    cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)
    sliced_map = get_sliced_map(cell_start_x, cell_start_y, cell_end_x, cell_end_y)

    block_set = set()
    for row in sliced_map:
        block_set |= (set(row))
    return block_set

def draw_map(is_draw_full=False):
    global _rect_inv_list

    if is_draw_full:
        _rect_inv_list.clear()
        _rect_inv_list.append(InvRect((SCREEN_WIDTH//2, SCREEN_HEIGHT//2), SCREEN_WIDTH, SCREEN_HEIGHT))
    elif len(_rect_inv_list) == 0:
        return

    # draw background
    for rect_inv in list(_rect_inv_list):
        if is_debug_mode():
            draw_debug_rect(rect_inv)

        if rect_inv.is_grid == False:
            block_set = get_block_set(rect_inv)
            if False not in block_set:
                rect_inv.is_filled = True
            elif True not in block_set:
                rect_inv.is_empty = True

        if rect_inv.is_filled:
            draw_ground(rect_inv)
            _rect_inv_list.remove(rect_inv)
            continue
        # empty
        elif rect_inv.is_empty:
            _rect_inv_list.remove(rect_inv)

        draw_background(rect_inv)

    # draw grounds
    for rect_inv in _rect_inv_list:
        cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)

        for cell_y in range(cell_start_y, cell_end_y + 1):
            for cell_x in range(cell_start_x, cell_end_x + 1):
                if out_of_range_cell(cell_x, cell_y):
                    continue
                elif get_block(cell_x, cell_y) == False:
                    continue

                posX, posY = get_pos_from_cell(cell_x, cell_y)
                originX, originY = get_origin_from_cell(cell_x, cell_y)

                _img_ground.clip_draw(originX, originY, CELL_SIZE, CELL_SIZE, posX, posY)


    _rect_inv_list.clear()



##### BLOCK #####
def create_block(radius, mouse_pos):
    draw_block(radius, mouse_pos, True)

def delete_block(radius, mouse_pos):
    draw_block(radius, mouse_pos, False)

def draw_block(radius, position, is_block):
    col, row = get_cell(position)
    x = -radius

    COLL_VAL = 0.5
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            cell_x = col+x
            cell_y = row+y
            if out_of_range_cell(cell_x, cell_y):
                continue
            elif get_block(cell_x, cell_y) == is_block:
                continue
            cell_pos = get_pos_from_cell(cell_x, cell_y)
            distance = (Vector2(*position) - Vector2(*cell_pos)).get_norm()
            if distance <= radius * CELL_SIZE + COLL_VAL:
                set_block(cell_x, cell_y, is_block)

    add_invalidate(position, radius*2 * CELL_SIZE, radius*2 * CELL_SIZE)




##### Invalidate #####
def resize_rect_inv(rect : Rect):
    if rect.left < 0:
        rect.set_origin((0, rect.bottom), rect.right, rect.height)
    elif rect.right > SCREEN_WIDTH:
        rect.set_origin((rect.left, rect.bottom), SCREEN_WIDTH - rect.left, rect.height)

    if rect.bottom <= MIN_HEIGHT:
        rect.set_origin((rect.left, MIN_HEIGHT), rect.width, rect.top - MIN_HEIGHT + 1)
    elif rect.top > SCREEN_HEIGHT:
        rect.set_origin((rect.left, rect.bottom), rect.width, SCREEN_HEIGHT - rect.bottom)
# merge rectangles
def merge_rects(rect_left : InvRect, rect_right : InvRect):
    width = rect_right.right - rect_left.left
    height = rect_right.top - rect_left.bottom
    center = (rect_left.left + width//2, rect_left.bottom + height//2)
    return InvRect(center, width, height, rect_left.is_filled, rect_left.is_empty)

_DEFAULT_DIVIDE_GRID_SIZE = CELL_SIZE * 7
_MIN_DIVIDE_GRID_SIZE = CELL_SIZE * 4
def set_invalidate_rect(center, width=0, height=0, scale=1, square=False, grid_size=_DEFAULT_DIVIDE_GRID_SIZE):
    CORR_VAL = 3

    width *= scale
    height *= scale
    width += CORR_VAL
    height += CORR_VAL

    if square:
        if width > height:
            height = width
        else:
            width = height
    
    add_invalidate(center, width, height, grid_size)

def add_invalidate(center, width, height, grid_size=_DEFAULT_DIVIDE_GRID_SIZE):
    global _rect_inv_list

    rect_inv = Rect.get_rect_int(Rect(center, width, height))
    rect_inv = InvRect(*rect_inv.__getitem__())

    resize_rect_inv(rect_inv)

    if grid_size == 0 or (rect_inv.width <= grid_size and rect_inv.height <= grid_size):
        rect_inv.is_grid = False
        _rect_inv_list.append(rect_inv)
        return

    # Divide rectangles by grid
    max_row = rect_inv.height//grid_size
    max_col = rect_inv.width//grid_size

    is_before_line_filled = False
    is_before_line_empty = False
    line_before : InvRect = None

    for row in range(0, max_row + 1):
        empty_count = 0
        filled_count = 0
        rect_before : InvRect = None

        for col in range(0, max_col + 1):
            x = rect_inv.origin[0] + (col*grid_size) + grid_size//2
            y = rect_inv.origin[1] + (row*grid_size) + grid_size//2
            width, height = grid_size, grid_size

            # remaining top area
            if row == max_row:
                height = int(rect_inv.height%grid_size)
                y = rect_inv.top - height//2
            # remaining right area
            if col == max_col:
                width = int(rect_inv.width%grid_size)
                x = rect_inv.right - width//2

            center = (x, y)
            rect = InvRect(center, width, height)

            # merge rect in row #
            block_set = get_block_set(rect)
            # filled
            if False not in block_set:
                if empty_count > 0:
                    _rect_inv_list.append(rect_before)
                empty_count = 0

                if filled_count > 0:
                    rect = merge_rects(rect_before, rect)
                filled_count += 1
                rect.is_filled = True
            # empty
            elif True not in block_set:
                if filled_count > 0:
                    _rect_inv_list.append(rect_before)

                filled_count = 0
                if empty_count > 0:
                    rect = merge_rects(rect_before, rect)
                empty_count += 1
                rect.is_empty = True
            else:
                if grid_size > _MIN_DIVIDE_GRID_SIZE:
                    add_invalidate(*rect.__getitem__(), _MIN_DIVIDE_GRID_SIZE)
                else:
                    _rect_inv_list.append(rect)
                if filled_count > 0 or empty_count > 0:
                    _rect_inv_list.append(rect_before)
                empty_count = 0
                filled_count = 0

            rect_before = rect

        # if filled_count > 0 or empty_count > 0:
        #     _rect_inv_list.append(rect_before)
        
        # merge rect by row #
        if filled_count > 0 or empty_count > 0:
            # row is filled
            if filled_count >= max_col:
                if is_before_line_empty:
                    _rect_inv_list.append(line_before)
                    line_before = None
                if line_before is None:
                    line_before = rect
                else:
                    line_before = merge_rects(line_before, rect)
                is_before_line_filled = True
                is_before_line_empty = False

            # row is empty
            elif empty_count > max_col:
                if is_before_line_filled:
                    _rect_inv_list.append(line_before)
                    line_before = None
                if line_before is None:
                    line_before = rect
                else:
                    line_before = merge_rects(line_before, rect)
                is_before_line_filled = False
                is_before_line_empty = True

            else:
                if line_before is not None:
                    _rect_inv_list.append(line_before)
                    line_before = None
                _rect_inv_list.append(rect_before)
                is_before_line_empty = False
                is_before_line_filled = False
        else:
            if line_before is not None:
                _rect_inv_list.append(line_before)
                line_before = None
            is_before_line_empty = False
            is_before_line_filled = False
    if line_before is not None:
        _rect_inv_list.append(line_before)









##### DEBUG #####
def draw_debugs():
    if len(_rect_debug_list) > 0:
        for rect in _rect_debug_list:
            draw_rectangle(rect.origin[0], rect.origin[1], rect.origin[0]+rect.width, rect.origin[1]+rect.height)
        _rect_debug_list.clear()
        
def draw_debug_cell(cell):
    r = CELL_SIZE//2
    pos = get_pos_from_cell(*cell)
    _rect_debug_list.append(Rect(pos, r, r))
def draw_debug_cells(cells):
    for cell in cells:
        draw_debug_cell(cell)
def draw_debug_vector(vector):
    _rect_debug_list.append(Rect(vector, 1, 1))
def draw_debug_vectors(vectors):
    for vector in vectors:
        draw_debug_vector(vector)
def draw_debug_point(point):
    _rect_debug_list.append(Rect(point, 2, 2))
def draw_debug_rect(rect : Rect):
    _rect_debug_list.append(rect)
    