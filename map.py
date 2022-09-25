from asyncio.windows_events import INFINITE
from math import degrees
from operator import inv
from pico2d import *
#from mytool import *
import mytool
import scene
import tank

img_debug : Image
img_debug_air : Image

LEFT = -1
RIGHT = 1

CELL_SIZE = 2

BLOCK_NONE = 0

BLOCK_DIRT = 1
BLOCK_PLACED_DIRT = -BLOCK_DIRT

BLOCK_DELETED = 999
BLOCK_DEBUG = 9999
BLOCK_DEBUG_AIR = 9998
BLOCK_PLACED_DEBUG = -BLOCK_DEBUG
BLOCK_PLACED_DEBUG_AIR = -BLOCK_DEBUG

BLOCK_SET = { BLOCK_PLACED_DEBUG, BLOCK_DIRT, BLOCK_PLACED_DIRT }

DEFAULT_RADIUS = 3
radius_draw = DEFAULT_RADIUS
is_draw_mode = False
is_create_block = False
is_delete_block = False
is_create_tank = False

crnt_map : list[list[int]]
xCellCount = 0
yCellCount = 0
is_map_invalid = True
invalid_rect : mytool.Rect = None

tank_obj : tank.Tank = None

def init():
    global img_debug, img_debug_air
    global xCellCount, yCellCount

    xCellCount = scene.screenWidth // CELL_SIZE
    yCellCount = scene.screenHeight // CELL_SIZE
    img_debug = mytool.load_image_path('debug.png')
    img_debug_air = mytool.load_image_path('debug_air.png')

## DRAW ##
def modify_map(events : list):
    global is_draw_mode, is_map_invalid
    global is_create_block, is_delete_block, is_create_tank
    global radius_draw
    global tank_obj

    if is_draw_mode == False:
        return
    
    event : Event
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == None:
                continue
            elif event.key == SDLK_RIGHT:
                if tank.tank_player1:
                    tank.tank_player1.start_move(RIGHT)
            elif event.key == SDLK_LEFT:
                if tank.tank_player1:
                    tank.tank_player1.start_move(LEFT)
            elif event.key == SDLK_F1:
                stop_draw_mode()
                return
            elif SDLK_1 <= event.key <= SDLK_9:
                radius_draw = event.key - SDLK_0
            elif event.key == SDLK_KP_MULTIPLY:
                radius_draw *= 2
            elif event.key == SDLK_KP_DIVIDE:
                radius_draw //= 2
            elif event.key == SDLK_F5:
                save_mapfile()
            elif event.key == SDLK_F9:
                if is_create_tank == False:
                    tank_obj = tank.Tank()
                else:
                    set_invalidate_rect(tank_obj.rect.center, tank_obj.rect.width, tank_obj.rect.height)
                is_create_tank = not is_create_tank
            continue
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_RIGHT:
                if tank.tank_player1:
                    tank.tank_player1.stop(RIGHT)
            elif event.key == SDLK_LEFT:
                if tank.tank_player1:
                    tank.tank_player1.stop(LEFT)
        elif event.type == SDL_MOUSEBUTTONDOWN:
            if event.button == SDL_BUTTON_LEFT:
                is_create_block = True
                if is_create_tank:
                    tank_obj.create()
                    is_create_tank = False
                    return
            elif event.button == SDL_BUTTON_RIGHT:
                is_delete_block = True
        elif event.type == SDL_MOUSEBUTTONUP:
            is_create_block = False
            is_delete_block = False
            continue

        mouse_pos = (-1, -1)
        if event.x != None:
            mouse_pos = mytool.convert_pico2d(event.x, event.y)

        if mouse_pos[0] < 0:
            continue
        if is_create_tank:
            tank_obj.set_pos(mouse_pos)
        elif is_create_block:
            create_block(radius_draw, mouse_pos)
        elif is_delete_block:
            delete_block(radius_draw, mouse_pos)
    
def start_draw_mode():
    global is_draw_mode
    is_draw_mode = True

def stop_draw_mode():
    global is_draw_mode, radius_draw
    radius_draw = DEFAULT_RADIUS
    is_draw_mode = False

def draw_map():
    global is_map_invalid

    if is_map_invalid == False:
        return

    start_x, start_y = invalid_rect.origin
    end_x = (start_x + invalid_rect.width)
    end_y = (start_y + invalid_rect.height)

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            if mytool.out_of_range(x, y, xCellCount, yCellCount):
                continue

            posX, posY = get_pos_from_index(x, y)
            block_type = crnt_map[y][x]

            if block_type == BLOCK_DELETED:
                srcX = posX - (CELL_SIZE//2)
                srcY = posY - (CELL_SIZE//2)
                scene.img_background.clip_draw(srcX, srcY, CELL_SIZE, CELL_SIZE, posX, posY, CELL_SIZE, CELL_SIZE)
                crnt_map[y][x] = BLOCK_NONE

            elif block_type == BLOCK_DIRT:
                scene.img_ground.draw(posX, posY, CELL_SIZE, CELL_SIZE)

            elif block_type == BLOCK_DEBUG:
                img_debug.draw(posX, posY, CELL_SIZE, CELL_SIZE)

            elif block_type == BLOCK_DEBUG_AIR:
                img_debug_air.draw(posX, posY, CELL_SIZE, CELL_SIZE)

            else:
                continue

            crnt_map[y][x] *= -1

    if tank_obj:
        tank_obj.draw()
    update_canvas()
    is_map_invalid = False

##### BLOCK #####
def create_block(radius, mouse_pos):
    set_block(radius, mouse_pos, BLOCK_DIRT)

def delete_block(radius, mouse_pos):
    set_block(radius, mouse_pos, BLOCK_DELETED)

def set_block(radius, mouse_pos, block_type):
    col, row = get_cell(mouse_pos)
    x = -radius

    for x in range(-radius, radius):
        for y in range(-radius, radius):
            if not mytool.out_of_range(col+x, row+y, xCellCount, yCellCount):
                crnt_map[row + y][col + x] = block_type

    invalidate(get_cell(mouse_pos), radius*2, radius*2)
    

##### Invalidate #####
def set_invalidate_rect(center, width=0, height=0, scale=1, square=False):
    global crnt_map
    
    center = mytool.to_int_pos(center)
    width *= scale
    height *= scale

    if square:
        if width > height:
            height = width
        else:
            width = height

    width = (width//CELL_SIZE) + CELL_SIZE
    height = (height//CELL_SIZE) + CELL_SIZE

    cell_center = get_cell(center)
    start_x, start_y = cell_center
    start_x -= width//2
    start_y -= height//2
    end_x = start_x + width
    end_y = start_y + height

    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            if not mytool.out_of_range(x, y, xCellCount, yCellCount):
                if crnt_map[y][x] == BLOCK_NONE:
                    crnt_map[y][x] = BLOCK_DELETED
                else:
                    crnt_map[y][x] *= -1
                #crnt_map[y][x] = BLOCK_DEBUG
    
    invalidate(cell_center, width, height)

def invalidate(cell_center, w, h):
    global is_map_invalid
    global invalid_rect
    w += CELL_SIZE
    h += CELL_SIZE
    invalid_rect = mytool.Rect(cell_center, w, h)
    is_map_invalid = True
    draw_map()

def invalidate_map():
    global invalid_rect
    invalid_rect = mytool.Rect()
    invalid_rect.set_origin((0,0), xCellCount, yCellCount)


##### Other #####
def get_cell(position):
    return (position[0]//CELL_SIZE), (position[1]//CELL_SIZE)

def get_pos_from_index(colIdx : int, rowIdx : int):
    return (colIdx * CELL_SIZE) + (CELL_SIZE//2), (rowIdx * CELL_SIZE) + (CELL_SIZE//2)

def get_cell_range(center, width, height, extra_range=0):
    width = (width//CELL_SIZE) + extra_range
    height = (height//CELL_SIZE) + extra_range

    start_x, start_y = get_cell(center)
    start_x -= width//2
    start_y -= height//2

    return start_x, start_y, start_x + width, start_y + height

def get_highest_ground_rect(rect : mytool.Rect, dir_down=True):
    global crnt_map

    width = int(rect.width//CELL_SIZE)
    height = int(rect.height//CELL_SIZE)

    start_x = int(rect.left//CELL_SIZE)
    start_y = int(rect.bottom//CELL_SIZE)
    end_x = int(start_x + width)

    if dir_down:
        for rowIdx in range(0, start_y).__reversed__():
            rows = crnt_map[rowIdx]
            set_row = set(rows[start_x:end_x])
            if set_row & BLOCK_SET:
                return rowIdx
    else:
        for rowIdx in range(start_y, (scene.screenHeight//CELL_SIZE) - 1):
            rows = crnt_map[rowIdx]
            set_row = set(rows[start_x:end_x])
            if not set_row & BLOCK_SET:
                if rowIdx == start_y:
                    return get_highest_ground_rect(rect, True)
                return rowIdx
    
    return -1

def get_highest_ground_point(x, y):
    global crnt_map, xCellCount, yCellCount

    col, row = get_cell((x, y))

    for y in range(0, row - 1).__reversed__():
        if not mytool.out_of_range(col, y, xCellCount, yCellCount) and is_block(crnt_map[y][col]):
            return (col, y)

    return False

def get_theta_rotate_ground(fRect : mytool.Rect):
        # 현재 위치는 떠 있으면 안됨
        # 회전 기준 -> center에 바닥이 없으면, 바닥이 없는 쪽(left or right)으로 회전

        rect = fRect.get_rect_int()
        center = rect.center[0], rect.bottom
        start_x, start_y, end_x, _ = get_cell_range(center, rect.width, 1, 1)
        center_x = start_x + (end_x - start_x)//2

        if mytool.out_of_range(start_x, start_y, xCellCount, yCellCount) \
            or crnt_map[start_y][center_x] != BLOCK_NONE:
            return False

        left_cells = crnt_map[start_y][start_x:center_x]
        right_cells = crnt_map[start_y][center_x + 1:end_x]
        is_left_empty = not set(left_cells) & BLOCK_SET
        is_right_empty = not set(right_cells) & BLOCK_SET

        cell_pivot = mytool.Vector2(-1 ,start_y)
        axis : mytool.Vector2

        max_length = 0
        if is_left_empty:
            for x in range(center_x + 1, end_x):
                if is_block(crnt_map[start_y][x]):
                    cell_pivot.x = x
                    break
            end_x = center_x
            max_length = (cell_pivot.x - start_x) * CELL_SIZE + 2
            axis = mytool.Vector2.left()

        elif is_right_empty:
            for x in range(start_x, center_x - 1).__reversed__():
                if is_block(crnt_map[start_y][x]):
                    cell_pivot.x = x
                    break
            start_x = center_x + 1
            max_length = (end_x - cell_pivot.x) * CELL_SIZE + 2
            axis = mytool.Vector2.right()

        else:
            return False

        if cell_pivot.x == -1:
            return False
            raise Exception

        vec_pivot = mytool.Vector2(cell_pivot.x * CELL_SIZE, rect.bottom)
        min_degree = INFINITE
        x_finds = set()
        #print("MAX : " + str(max_length))
        #print("\n\npivot : " + str(vec_pivot))
        for y in range(0, start_y - 1).__reversed__():
            x_counts = end_x - start_x
            for x in range(start_x, end_x):
                if x in x_finds:
                    x_counts -= 1
                    continue
                elif is_block(crnt_map[y][x]):
                    vec_dest = mytool.Vector2(x * CELL_SIZE, y * CELL_SIZE)
                    length = mytool.get_length(vec_pivot.x, vec_pivot.y, vec_dest.x, vec_dest.y)
                    x_finds.add(x)
                    if length > max_length:
                        continue

                    degree = math.degrees(vec_dest.get_theta(axis, vec_pivot))
                    if axis == mytool.Vector2.right():
                        degree *= -1
                    #print("dest : " + str(vec_dest))
                    #print("degree : " + str(degree))
                    if math.fabs(degree) < math.fabs(min_degree):
                        min_degree = degree
                        #print("min_degree : " + str(min_degree))
                        crnt_map[y][x] = BLOCK_DEBUG
            if x_counts <= 0:
                break

        # Fall
        if min_degree == INFINITE:
            if is_left_empty:
                return math.radians(90)
            else:
                return math.radians(-90)

        #print("result_degree : " + str(min_degree))
        return math.radians(min_degree)

def is_block(block):
    return block in BLOCK_SET

##### FILE I/O #####
def read_mapfile(index : int):
    global crnt_map

    fileName = 'map' + str(index) + '.txt'
    file = open('maps/' + fileName, 'r')

    crnt_map = [[0]*xCellCount for col in range(yCellCount)]
    for rowIdx, row in enumerate(crnt_map):
        line = file.readline()
        for idx, ch in enumerate(line):
            if ch == '\n':
                break
            crnt_map[rowIdx][idx] = int(ch)

    file.close()

def save_mapfile():
    global crnt_map, xCellCount, yCellCount

    fileName = 'map_save' + '.txt'
    file = open('maps/' + fileName, 'w')

    for row in crnt_map:
        for col in row:
            if col < 0:
                col *= -1
            file.write(str(col))
        file.write('\n')
    
    file.close()