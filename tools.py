from pico2d import *
import math
import random

_is_debug_mode = False

CELL_SIZE = 2   # recommend an even number (min : 2)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 1000
MIN_HEIGHT = 108

X_CELL_COUNT = SCREEN_WIDTH // CELL_SIZE
Y_CELL_COUNT = (SCREEN_HEIGHT-MIN_HEIGHT) // CELL_SIZE
Y_CELL_MIN = MIN_HEIGHT//CELL_SIZE

LEFT = -1
RIGHT = 1

_crnt_map : list[list[bool]] = []

class Vector2:
    def __init__(self, x=0, y=0):
        self.x : float = x
        self.y : float = y

    def __call__(self):
        return self.x, self.y
    
    def __getitem__(self):
        return (self.x, self.y)
    
    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)
    
    def __truediv__(self, other : float):
        return Vector2(self.x / other, self.y / other)
    
    def __eq__(self, other):
        return (self.x == other.x and self.y == other.y)

    def left():
        return Vector2(-1, 0)
    def right():
        return Vector2(1, 0)
    def up():
        return Vector2(0, 1)
    def down():
        return Vector2(0, -1)
    def zero():
        return Vector2(0, 0)

    def normalize(self):
        norm = self.get_norm()
        self /= norm

    def normalized(self):
        norm = self.get_norm()
        self /= norm
        return self

    def get_norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y)
    
    def cross(self):
        return Vector2(-self.y, self.x)
    
    def get_theta(self, other):
        dot = self.dot(other)
        return math.acos(dot / (self.get_norm() * other.get_norm()))

    def get_theta_axis(self, axis, origin):
        self -= origin
        dot = self.dot(axis)
        return math.acos(dot / (self.get_norm() * axis.get_norm()))

    def get_dest(self, vector_dir, speed : float):
        return self + (vector_dir * speed)

    # rotate self(unit direction vector) to vec_dest
    def get_rotated_dest(self, vec_src, vec_dest, t=1): # t=0~1
        vec_to_target = (vec_dest - vec_src).normalized()
        a = math.atan2(self.x, self.y)
        b = math.atan2(vec_to_target.x, vec_to_target.y)
        theta = a - b

        return self.get_rotated(theta * t)
    def get_rotated(self, theta):
        result = Vector2()
        result.x = (self.x * math.cos(theta)) - (self.y * math.sin(theta))
        result.y = (self.x * math.sin(theta)) + (self.y * math.cos(theta))

        return result

    def get_rotated_origin(self, origin, theta):
        if type(origin) != Vector2:
            origin = Vector2(*origin)

        result = self
        result -= origin
        
        return origin + result.get_rotated(theta)
    
    def lerp(self, dst, t):
        transform = Vector2()
        transform.x = (self.x * (1 - t)) + (dst.x * t)
        transform.y = (self.y * (1 - t)) + (dst.y * t)
        return transform
        

class Rect:
    def __init__(self, center=(0,0), width=0, height=0):
        self.center : tuple = center
        self.origin : tuple = (0,0)
        self.width : float = width
        self.height : float = height

        self.left : float = 0
        self.right : float = 0
        self.top : float = 0
        self.bottom : float = 0

        self.set_pos(center)

    def __getitem__(self):
        return (self.center, self.width, self.height)
    
    def set_origin(self, origin, width, height):
        self.width = width
        self.height = height
        self.origin = origin
        self.center = [origin[0] + (self.width//2), origin[1] + (self.height//2)]
        self.set_pos(self.center)

    def set_pos(self, center):
        self.center = center
        self.left = center[0] - (self.width//2)
        self.right = center[0] + (self.width//2)
        self.top = center[1] + (self.height//2)
        self.bottom = center[1] - (self.height//2)
        self.origin = (self.left, self.bottom)
    
    def get_rect_int(self):
        result = Rect()
        result.center = to_int_pos(self.center)
        result.width = int(self.width)
        result.height = int(self.height)
        result.update()
        return result

    def get_fCenter(self):
        return [self.origin[0] + (self.width/2), self.origin[1] + (self.height/2)]

    def update(self):
        self.set_pos(self.center)
        
    def collide_point(self, x, y):
        if x >= self.left and x <= self.right and y >= self.bottom and y <= self.top:
            return True
        return False
    
    def move(self, x, y):
        self.center = (self.center[0] + x, self.center[1] + y)
        self.update()

    def get_copy(self):
        result = Rect()
        result.center = self.center
        result.width = self.width
        result.height = self.height
        result.update()
        return result

# Invalidation Rectangle
class InvRect(Rect):
    def __init__(self, center=(0,0), width=0, height=0, is_filled=False, is_empty=False):
        super().__init__(center, width, height)
        self.is_filled = is_filled
        self.is_empty = is_empty
        self.is_grid = True


##### TOOLS #####
def convert_pico2d(x, y):
    return x, SCREEN_HEIGHT - 1 - y
    
def load_image_path(image : str):
    name = 'images/' + image
    result = load_image(name)
    print('load : ' + name)
    return result

def out_of_range(x, y, max_x, max_y):
    return ((x < 0) or (x >= max_x) or (y < 0) or (y >= max_y))
def out_of_range_cell(cell_x, cell_y):
    return ((cell_x < 0) or (cell_x >= X_CELL_COUNT) or (cell_y < 0) or (cell_y >= Y_CELL_COUNT))

def get_length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def to_int_pos(position):
    return (int(position[0]), int(position[1]))

def get_sign(num):
    return num / math.fabs(num)
def is_debug_mode():
    return _is_debug_mode
def toggle_debug_mode():
    global _is_debug_mode
    _is_debug_mode = not _is_debug_mode


##### MAP #####
def get_cell(position):
    return int(position[0]//CELL_SIZE), int((position[1]-MIN_HEIGHT)//CELL_SIZE)
def get_cells(positions):
    result = []
    for pos in positions:
        result.append(get_cell(pos))
    return result

def get_pos_from_cell(colIdx : int, rowIdx : int):
    return ((colIdx * CELL_SIZE) + CELL_SIZE//2), ((rowIdx * CELL_SIZE) + CELL_SIZE//2) + MIN_HEIGHT
def get_origin_from_cell(colIdx : int, rowIdx : int):
    return ((colIdx * CELL_SIZE) + CELL_SIZE//2) - CELL_SIZE//2, ((rowIdx * CELL_SIZE) + CELL_SIZE//2) - CELL_SIZE//2 + MIN_HEIGHT

# def get_cell_range(center, width, height, extra_range=0):
#     width = (width//CELL_SIZE) + extra_range
#     height = (height//CELL_SIZE) + extra_range

#     start_x, start_y = get_cell(center)
#     start_x -= width//2
#     start_y -= height//2

#     return start_x, start_y, start_x + width, start_y + height

def get_block(cell):
    if out_of_range_cell((cell[0], cell[1])):
        return False
    return _crnt_map[cell[1]][cell[0]]

def get_detected_cells(rect : Rect):
    global _crnt_map
    result = []
    cell_start_x, cell_start_y, cell_end_x, cell_end_y = get_start_end_cells(rect)
    for cell_y in range(cell_start_y, cell_end_y + 1):
        for cell_x in range(cell_start_x, cell_end_x + 1):
            if out_of_range_cell(cell_x, cell_y):
                continue
            block = _crnt_map[cell_y][cell_x]
            if block:
                result.append((cell_x, cell_y))
    
    return result
                
def get_start_end_cells(rect : Rect):
    cell_start_x, cell_start_y = get_cell(rect.origin)
    cell_end_x, cell_end_y = get_cell( (rect.origin[0] + rect.width, rect.origin[1] + rect.height) )
    return cell_start_x, cell_start_y, cell_end_x, cell_end_y

def get_block(col : int, row : int):
    return _crnt_map[row][col]
def get_block_cell(cell : tuple):
    return _crnt_map[cell[1]][cell[0]]
def set_block(col : int, row : int, is_block : bool):
    if type(is_block) is not bool:
        pass
    _crnt_map[row][col] = is_block

# end is inclusive
def get_sliced_map(start_x, start_y, end_x, end_y):
    if start_x < 0:
        start_x = 0
    if end_x >= X_CELL_COUNT:
        end_x = X_CELL_COUNT - 1
    if start_y < 0:
        start_y = 0
    if end_y >= Y_CELL_COUNT:
        end_y = Y_CELL_COUNT - 1
    
    return [_crnt_map[i][start_x:end_x + 1] for i in range(start_y, end_y + 1)]


##### Object #####
def get_highest_ground_cell(x, y, max_length = float('inf'), is_cell=False):
    global _crnt_map

    cell_start_col, cell_start_row = int(x), int(y)
    if not is_cell:
        cell_start_col, cell_start_row = get_cell((x, y))
    
    max_length /= CELL_SIZE

    dir_down = True
    if out_of_range_cell(cell_start_col, cell_start_row):
        return False
    elif _crnt_map[cell_start_row][cell_start_col]:
        dir_down = False

    if dir_down:
        for row in range(0, cell_start_row + 1).__reversed__():
            if not out_of_range_cell(cell_start_col, row) and _crnt_map[row][cell_start_col]:
                if (cell_start_row - row) > max_length:
                    break
                return (cell_start_col, row)
    else:
        for row in range(cell_start_row + 1, Y_CELL_COUNT):
            if not out_of_range_cell(cell_start_col, row) and not _crnt_map[row][cell_start_col]:
                if (row - cell_start_row) > max_length:
                    break
                return (cell_start_col, row - 1)

    return False











##### FILE I/O #####
def read_mapfile(index : int):
    from gmap import img_background
    global _crnt_map, img_map

    _crnt_map = [[False]*X_CELL_COUNT for col in range(Y_CELL_COUNT)]

    if index == -1:
        img_background.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)    # Empty background
        return

    fileName = 'map_' + str(index) + '.txt'
    file = open('maps/' + fileName, 'r')

    for rowIdx, row in enumerate(_crnt_map):
        line = file.readline()
        for colIdx, ch in enumerate(line):
            if colIdx >= X_CELL_COUNT:
                break
            _crnt_map[rowIdx][colIdx] = bool(int(ch))

    file.close()

    img_map = load_image_path('map_' + str(index) + '.png')
    img_map.draw(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + Y_CELL_MIN)

def save_mapfile():
    global _crnt_map, X_CELL_COUNT, Y_CELL_COUNT

    fileName = 'map_save' + '.txt'
    file = open('maps/' + fileName, 'w')

    for row in _crnt_map:
        for col in row:
            file.write(str(int(col)))
        file.write('\n')
    
    file.close()