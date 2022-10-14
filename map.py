if __name__ == "__main__":
    quit()

from tools import *
from object import *
import scene
import tank

img_map : Image
img_debug : Image
img_debug_air : Image

DEFAULT_RADIUS = 3
radius_draw = DEFAULT_RADIUS
is_draw_mode = False
is_create_block = False
is_delete_block = False
is_print_mouse_pos = False

crnt_map : list[list[int]]
xCellCount = 0
yCellCount = 0
rect_inv_list : list[Rect] = []

tank_obj : tank.Tank = None


def init():
    global img_debug, img_debug_air
    global xCellCount, yCellCount

    # 1 ~ screen_max
    xCellCount = scene.screenWidth // CELL_SIZE
    yCellCount = scene.screenHeight // CELL_SIZE
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
                    gameObjects.append(tank_obj)
                else:
                    set_invalidate_rect(*tank_obj.get_rect().__getitem__())
                    gameObjects.remove(tank_obj)
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
    radius_draw = DEFAULT_RADIUS
    is_draw_mode = False

def draw_map(is_draw_full=False):
    global rect_inv_list

    if is_draw_full:
        rect_inv_list.clear()
        rect_inv_list.append(Rect((scene.screenWidth//2, scene.screenHeight//2), scene.screenWidth, scene.screenHeight))
    elif len(rect_inv_list) == 0:
        return

    # draw background
    for rect_inv in rect_inv_list:
        scene.img_background.clip_draw(int(rect_inv.origin[0]), int(rect_inv.origin[1] - scene.min_height), int(rect_inv.width), int(rect_inv.height), *rect_inv.get_fCenter())
        if DEBUG:
            draw_rectangle(rect_inv.origin[0], rect_inv.origin[1], rect_inv.origin[0] + int(rect_inv.width), rect_inv.origin[1] + int(rect_inv.height))

    # draw grounds
    block_counts = []
    for rect_inv in rect_inv_list:
        block_count = 0        
        cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect_inv)

        for cell_y in range(cell_start_y, cell_end_y + 1):
            for cell_x in range(cell_start_x, cell_end_x + 1):
                if out_of_range(cell_x, cell_y, xCellCount, yCellCount):
                    continue
                block_type = crnt_map[cell_y][cell_x]
                if block_type == BLOCK_NONE:
                    continue

                posX, posY = get_pos_from_cell(cell_x, cell_y)
                originX, originY = get_origin_from_cell(cell_x, cell_y)

                if block_type == BLOCK_GROUND:
                    scene.img_ground.clip_draw(originX, originY, CELL_SIZE, CELL_SIZE, posX, posY)
                    crnt_map[cell_y][cell_x] = -BLOCK_GROUND
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
                elif out_of_range(cell_x, cell_y, xCellCount, yCellCount):
                    continue
                elif crnt_map[cell_y][cell_x] < 0:
                    crnt_map[cell_y][cell_x] *= -1
                    block_count -= 1
            if is_end:
                break

    rect_inv_list.clear()



##### BLOCK #####
def create_block(radius, mouse_pos):
    set_block(radius, mouse_pos, BLOCK_GROUND)

def delete_block(radius, mouse_pos):
    set_block(radius, mouse_pos, BLOCK_NONE)

def set_block(radius, position, block_type):
    col, row = get_cell(position)
    x = -radius

    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            cell_x = col+x
            cell_y = row+y
            if out_of_range(cell_x, cell_y, xCellCount, yCellCount):
                continue
            elif row + y < scene.min_height // CELL_SIZE:
                continue
            cell_pos = get_pos_from_cell(cell_x, cell_y)
            distance = (Vector2(*position) - Vector2(*cell_pos)).get_norm()
            if distance <= radius * CELL_SIZE:
                crnt_map[row + y][col + x] = block_type

    add_invalidate(position, radius*2 * CELL_SIZE, radius*2 * CELL_SIZE)

# def set_block(radius, position, block_type):
#     col, row = get_cell(position)
#     x = -radius

#     for x in range(-radius, radius + 1):
#         for y in range(-radius, radius + 1):
#             if not out_of_range(col+x, row+y, xCellCount, yCellCount):
#                 if row + y >= scene.min_height // CELL_SIZE:
#                     crnt_map[row + y][col + x] = block_type

#     add_invalidate(position, radius*2 * CELL_SIZE, radius*2 * CELL_SIZE)
    
def is_block(block):
    return block in BLOCK_SET
def is_block_cell(cell):
    return crnt_map[cell[1]][cell[0]] in BLOCK_SET





##### Invalidate #####
# BUG : Distortion background when move tank
def set_invalidate_rect(center, width=0, height=0, scale=1, square=False):
    global crnt_map
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
    elif rect_inv.right > scene.screenWidth:
        rect_inv.set_origin((rect_inv.left, rect_inv.bottom), scene.screenWidth - rect_inv.left, rect_inv.height)

    if rect_inv.bottom <= scene.min_height:
        rect_inv.set_origin((rect_inv.left, scene.min_height), rect_inv.width, rect_inv.top - scene.min_height + 1)
    elif rect_inv.top > scene.screenHeight:
        rect_inv.set_origin((rect_inv.left, rect_inv.bottom), rect_inv.width, scene.screenHeight - rect_inv.bottom)

    rect_inv_list.append(rect_inv)




##### Tools #####
def get_cell(position):
    return int(position[0]//CELL_SIZE), int(position[1]//CELL_SIZE)
def get_cells(positions):
    result = []
    for pos in positions:
        result.append(get_cell(pos))
    return result

def get_pos_from_cell(colIdx : int, rowIdx : int):
    return ((colIdx * CELL_SIZE) + CELL_SIZE//2), ((rowIdx * CELL_SIZE) + CELL_SIZE//2)
def get_origin_from_cell(colIdx : int, rowIdx : int):
    return ((colIdx * CELL_SIZE) + CELL_SIZE//2) - CELL_SIZE//2, ((rowIdx * CELL_SIZE) + CELL_SIZE//2) - CELL_SIZE//2

def get_cell_range(center, width, height, extra_range=0):
    width = (width//CELL_SIZE) + extra_range
    height = (height//CELL_SIZE) + extra_range

    start_x, start_y = get_cell(center)
    start_x -= width//2
    start_y -= height//2

    return start_x, start_y, start_x + width, start_y + height

def get_block(cell):
    if out_of_range(cell[0], cell[1], xCellCount, yCellCount):
        return False
    return crnt_map[cell[1]][cell[0]]

def get_detected_cells(rect : Rect):
    result = []
    cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect)
    for cell_y in range(cell_start_y, cell_end_y + 1):
        for cell_x in range(cell_start_x, cell_end_x + 1):
            if out_of_range(cell_x, cell_y, xCellCount, yCellCount):
                continue
            cell = crnt_map[cell_y][cell_x]
            if is_block(cell):
                result.append((cell_x, cell_y))
    
    return result
                
def get_start_end_cells(rect : Rect):
    cell_start_x, cell_start_y = get_cell(rect.origin)
    cell_end_x, cell_end_y = get_cell( (rect.origin[0] + rect.width, rect.origin[1] + rect.height) )
    return cell_start_x, cell_start_y, cell_end_x, cell_end_y

def out_of_range_cell(cell):
    return ((cell[0] < 0) or (cell[0] >= xCellCount) or (cell[1] < 0) or (cell[1] >= yCellCount))





##### Object #####
def get_highest_ground_point(x, y, max_length, is_cell=False):
    global crnt_map, xCellCount, yCellCount

    cell_start_col, cell_start_row = int(x), int(y)
    if not is_cell:
        cell_start_col, cell_start_row = get_cell((x, y))
    
    max_length /= CELL_SIZE

    dir_down = True
    if out_of_range(cell_start_col, cell_start_row, xCellCount, yCellCount):
        return False
    elif is_block(crnt_map[cell_start_row][cell_start_col]):
        dir_down = False

    if dir_down:
        for row in range(scene.min_height, cell_start_row + 1).__reversed__():
            if not out_of_range(cell_start_col, row, xCellCount, yCellCount) and is_block(crnt_map[row][cell_start_col]):
                if (cell_start_row - row) > max_length:
                    break
                return (cell_start_col, row)
    else:
        max_row = scene.screenHeight//CELL_SIZE
        for row in range(cell_start_row + 1, max_row):
            if not out_of_range(cell_start_col, row, xCellCount, yCellCount) and not is_block(crnt_map[row][cell_start_col]):
                if (row - cell_start_row) > max_length:
                    break
                return (cell_start_col, row - 1)

    # Fall
    return False


def get_vec_highest(object : GroundObject):
    vectors_bot = object.get_vectors_bot()
    bot_cells = get_cells(vectors_bot)

    vec_highest = Vector2.zero()
    vec_befroe : Vector2 = None

    max_length = object.get_rect().width
    idx_highest = 0
    if object.is_created == False:
        max_length = float('inf')
    for idx, cell in enumerate(bot_cells):
        result = get_highest_ground_point(cell[0], cell[1], max_length, True)
        if result is False:
            continue
        
        col, row = result
        _, height = get_pos_from_cell(col, row)
        if height > vec_highest.y:
            vec_highest.x = vectors_bot[idx].x
            vec_highest.y = height
            vec_befroe = vectors_bot[idx]
            idx_highest = idx

    return vec_befroe, vec_highest, idx_highest

def attach_to_ground(object : GroundObject):
    vec_befroe, vec_pivot, idx_pivot = get_vec_highest(object)
    if vec_befroe is None:
        return False, False

    dy = vec_pivot.y - vec_befroe.y
    object.offset(0, dy)

    return vec_pivot, idx_pivot

def get_rotated_to_ground(object : GroundObject):
    vec_pivot, idx_pivot = attach_to_ground(object)
    if vec_pivot is False:
        return False
    vectors_bot = object.get_vectors_bot()

    # set rotation direction
    dir_check = LEFT
    if vec_pivot.x < object.bot_center.x:
        dir_check = RIGHT
        
    axis = Vector2()
    if dir_check == LEFT:
        axis = Vector2.left()
    else:
        axis = Vector2.right()

    max_y = object.bot_center.y + object.width//2
    min_y = object.bot_center.y - object.width//2
    # get minimum theta
    min_theta = float("inf")
    for vector in vectors_bot:
        if dir_check == RIGHT:
            if vector.x < object.bot_center.x:
                continue
        else:
            if vector.x > object.bot_center.x:
                continue

        cell = get_cell(vector)
        if out_of_range(cell[0], cell[1], xCellCount, yCellCount):
            continue

        ground_cell = get_highest_ground_point(*cell, object.width, True)
        if ground_cell is False:
            continue
            
        vec_ground = Vector2(*get_pos_from_cell(*ground_cell))
        if vec_ground.y == vec_pivot.y:
            continue

        # max_length = (vec_pivot - vector).get_norm() + 4
        # length = (vec_pivot - vec_ground).get_norm()
        # if length > max_length:
        #     continue
        if vec_ground.y > max_y or vec_ground.y < min_y:
            continue
        
        theta = vec_ground.get_theta_axis(axis, vec_pivot)
        if dir_check == RIGHT:
            theta *= -1

        if math.fabs(theta) < math.fabs(min_theta):
            min_theta = theta
    
    # didn't find highest ground point for bottom vectors   
    if min_theta == float("inf"):
        min_theta = object.theta * 0.9
    elif math.fabs(math.degrees(min_theta)) > 75:
        return False

    # ground와 object의 거리 계산하여 크면 False


    # rotation and set position to ground
    object.set_theta(min_theta)
    vectors_bot = object.get_vectors_bot()
    vector_correction = (vec_pivot - vectors_bot[idx_pivot]) 
    object.set_center((object.center[0] + vector_correction[0], object.center[1] + vector_correction[1]))

    if is_floating(object):
        attach_to_ground(object)

    # move if position is not on the edge
    for vector in vectors_bot:
        if object.dir == RIGHT:
            if vector.x < object.bot_center.x:
                continue
        else:
            if vector.x > object.bot_center.x:
                continue
        
        cell = get_cell(vector)
        result = get_highest_ground_point(*cell, object.width, True)
        if result is not False:
            return True

    return False


def is_floating(object : GameObject):
    vectors_bot = object.get_vectors_bot()
    for vector in vectors_bot:
        cell = get_cell(vector)
        if is_block_cell(cell):
            return False
        
    return True














##### DEBUG #####
def draw_debug_cell(cell):
    r = CELL_SIZE//2
    pos = get_pos_from_cell(*cell)
    draw_rectangle(pos[0]-r,pos[1]-r,pos[0]+r,pos[1]+r)
def draw_debug_cells(cells):
    for cell in cells:
        draw_debug_cell(cell)
def draw_debug_vector(vector):
    draw_rectangle(vector.x, vector.y, vector.x, vector.y)
def draw_debug_vectors(vectors):
    for vector in vectors:
        draw_debug_vector(vector)
def draw_debug_point(point):
    rect = Rect(point, 2, 2)
    draw_rectangle(rect.left, rect.bottom, rect.right, rect.top)


##### FILE I/O #####
def read_mapfile(index : int):
    global crnt_map, img_map

    crnt_map = [[0]*xCellCount for col in range(yCellCount)]

    if index == -1:
        scene.img_background.draw(scene.screenWidth//2, scene.screenHeight//2 + scene.min_height//2)    # Empty background
        return

    fileName = 'map_' + str(index) + '.txt'
    file = open('maps/' + fileName, 'r')

    for rowIdx, row in enumerate(crnt_map):
        line = file.readline()
        for colIdx, ch in enumerate(line):
            if colIdx >= xCellCount:
                break
            crnt_map[rowIdx][colIdx] = int(ch)

    file.close()

    img_map = load_image_path('map_' + str(index) + '.png')
    img_map.draw(scene.screenWidth//2, scene.screenHeight//2 + scene.min_height//2)

def save_mapfile():
    global crnt_map, xCellCount, yCellCount

    fileName = 'map_save' + '.txt'
    file = open('maps/' + fileName, 'w')

    for row in crnt_map:
        for col in row:
            file.write(str(col))
        file.write('\n')
    
    file.close()
