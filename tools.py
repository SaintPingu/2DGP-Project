from asyncio.windows_events import INFINITE
from pico2d import *
import math

DEBUG = False

LEFT = -1
RIGHT = 1

CELL_SIZE = 2

BLOCK_NONE = 0
BLOCK_GROUND = 1

BLOCK_DEBUG = 9999
BLOCK_DEBUG_AIR = 9998

BLOCK_SET = { BLOCK_DEBUG, BLOCK_GROUND }


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
    
    def cross(self, other):
        return Vector2(-self.y, other.x)
    
    def get_theta(self, other):
        dot = self.dot(other)
        return math.acos(dot / (self.get_norm() * other.get_norm()))

    def get_theta_axis(self, axis, origin):
        self -= origin
        dot = self.dot(axis)
        return math.acos(dot / (self.get_norm() * axis.get_norm()))

    def get_dest(self, vector_dir, speed : float):
        return self + (vector_dir * speed)

    def rotate(self, theta):
        self = self.get_rotated(theta)

    # does not work
    # def rotate_origin(self, origin, theta):
    #     self = self.get_rotated_origin(origin, theta)

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

    def get_rotated_vDir(self, vDest, vDir, t:float=1):
        if t < 0:
            t = 0
        elif t > 1:
            t = 1

        vToTarget = (vDest - self).normalized()
        a = math.atan2(vDir.x, vDir.y)
        b = math.atan2(vToTarget.x, vToTarget.y)
        theta = a - b

        rot_degree = math.degrees(theta)
        if(math.fabs(rot_degree) > 180):
            rot_degree -= get_sign(rot_degree) * 360
        if(math.fabs(rot_degree) > 45):
            rot_degree = get_sign(rot_degree) * 45
        vDir = self.get_rotated(vDir, math.radians(rot_degree))
        return vDir
    
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

class GameObject:
    def __init__(self, center=(0,0), width=0, height=0, theta=0):
        self.center : Vector2 = Vector2(*center)
        self.width : float = width
        self.height : float = height

        self.bot_left = Vector2()
        self.bot_right = Vector2()
        self.top_left = Vector2()
        self.top_right = Vector2()
        self.bot_center = Vector2()

        self.rot_theta : float = theta
        self.is_invalid_rect : bool = True
        self.is_created : bool = False

        self.dir : int = 0
        self.speed : float = 1

        self.update_object()

    def update_object(self):
        self.bot_left.x = self.top_left.x = self.center.x - self.width//2
        self.bot_left.y = self.bot_right.y = self.center.y - self.height//2
        self.bot_right.x = self.top_right.x =  self.center.x + self.width//2
        self.top_left.y = self.top_right.y = self.center.y + self.height//2
        
        self.bot_left = self.bot_left.get_rotated_origin(self.center, self.rot_theta)
        self.bot_right = self.bot_right.get_rotated_origin(self.center, self.rot_theta)
        self.top_left = self.top_left.get_rotated_origin(self.center, self.rot_theta)
        self.top_right = self.top_right.get_rotated_origin(self.center, self.rot_theta)

        vec_left_to_center = (self.bot_right - self.bot_left).normalized() * (self.width // 2)
        self.bot_center = self.bot_left + vec_left_to_center
        self.is_invalid_rect = True

    def rotate(self, theta):
        self.rot_theta += theta
        self.update_object()

    def set_theta(self, theta):
        self.rot_theta = theta
        self.update_object()

    def rotate_pivot(self, theta, pivot):
        center = self.center
        self.center = center.get_rotated_origin(pivot, theta)
        self.rot_theta = theta
        self.update_object()

    def offset(self, dx, dy):
        self.center.x += dx
        self.center.y += dy
        self.update_object()

    def set_center(self, center):
        self.center = Vector2(*center)
        self.update_object()

    def draw_image(self, image : Image):
        if self.is_invalid_rect == False:
            return
        self.is_invalid_rect = False
        image.rotate_draw(self.rot_theta, *self.center)

    def get_rect(self):
        return Rect(self.center, self.width, self.height)

    def get_vec_left(self):
        return (self.bot_left - self.bot_right).normalized()
    def get_vec_right(self):
        return (self.bot_right - self.bot_left).normalized()
    
    def out_of_bound(self, left= -9999, top= -9999, right= -9999, bottom= -9999):
        rect = self.get_rect()

        if left != -9999 and rect.left < left:
            return True
        elif top != -9999 and rect.top > top:
            return True
        elif right != -9999 and rect.right > right:
            return True
        elif bottom != -9999 and rect.bottom < bottom:
            return True

        return False

    def set_pos(self, center):
        self.set_center(center)

    def draw_debug_rect(self):
        rect = self.get_rect()
        draw_rectangle(rect.left, rect.bottom, rect.right, rect.top)




class GroundObject(GameObject):
    def get_vectors_bot(self):
        t = 0
        inc_t = 1 / self.width

        result : list[Vector2] = []
        while t <= 1:
            position = self.bot_left.lerp(self.bot_right, t)
            result.append(position)
            t += inc_t

        return result

    def move(self):
        if self.dir == 0:
            return
        elif self.dir == LEFT:
            self.vDir = self.get_vec_left()
        else:
            self.vDir = self.get_vec_right()

        vDest = self.center + (self.vDir * self.speed)

        if self.set_pos(vDest) == False:
            self.stop()

    def start_move(self, dir):
        self.dir += dir

    def stop(self):
        self.dir = 0











def convert_pico2d(x, y):
    from scene import screenHeight
    return x, screenHeight - 1 - y
    
def load_image_path(image : str):
    name = 'images/' + image
    result = load_image(name)
    print('load : ' + name)
    return result

def out_of_range(x, y, max_x, max_y):
    return ((x < 0) or (x >= max_x) or (y < 0) or (y >= max_y))

def get_length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def to_int_pos(position):
    return (int(position[0]), int(position[1]))

def get_sign(num):
    return num / math.fabs(num)