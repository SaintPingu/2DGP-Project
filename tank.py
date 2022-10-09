from tools import *
from object import *
import map
import shell

tank_green : Image = None
barrel_green : Image = None

def init():
    global tank_green, barrel_green
    tank_green = load_image_path('tank_green.png')
    barrel_green = load_image_path('barrel_green.png')

class Tank(GroundObject):
    def __init__(self, center=(0,0)):
        global tank_player1

        if tank_player1:
            map.set_invalidate_rect(*tank_player1.get_rect().__getitem__())
            tank_player1 = None

        self.img_tank = tank_green
        self.img_barrel = barrel_green

        self.barrel_position = Vector2()
        self.barrel_pivot = Vector2()
        self.barrel_theta = 0
        self.hp = 100

        super().__init__(center, self.img_tank.w, self.img_tank.h)

        tank_player1 = None

    def set_pos(self, center):
        def dont_move(prev_theta, prev_center):
            self.set_theta(prev_theta)
            self.set_center(prev_center)

        from scene import screenHeight, screenWidth

        prev_rect = self.get_rect()
        prev_theta = self.theta

        self.set_center(center)
        if self.out_of_bound(0, screenHeight, screenWidth, 0):
            dont_move(prev_theta, prev_rect.center)
            return False

        # don't move if collision by the wall
        if self.dir != 0:
            vectors_coll = self.get_collision_vectors()
            for vector in vectors_coll:
                cell = map.get_cell(vector)
                block = map.get_block(cell)
                if block is not False and map.is_block(block):
                    dont_move(prev_theta, prev_rect.center)
                    return False

        if map.get_rotated_to_ground(self) == False:
            dont_move(prev_theta, prev_rect.center)
            return False
        
        prev_barrel_rect = self.update_barrel()
        map.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True)
        map.set_invalidate_rect(*prev_rect.__getitem__(), square=True)
        self.is_rect_invalid = True

        return True

    def draw(self):
        if self.is_rect_invalid == False:
            return
        
        self.img_barrel.rotate_draw(self.barrel_theta, *self.barrel_position)
        self.draw_image(self.img_tank)

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True
        self.is_setting_mode = False

    def update(self):
        self.move()

    def update_barrel(self):
        prev_barrel_rect = Rect(self.barrel_position, self.img_barrel.w, self.img_barrel.h)
        self.barrel_position = self.barrel_pivot
        self.barrel_position.x += self.img_barrel.w / 2

        vNormal = Vector2.cross(self.bot_left, self.bot_right).normalized()
        self.barrel_pivot = Vector2(*self.get_rect().center) + (vNormal * 3)
        self.barrel_position.y = self.barrel_pivot.y
        self.barrel_position = self.barrel_position.get_rotated_origin(self.barrel_pivot, self.barrel_theta)
        return prev_barrel_rect


    def get_collision_vectors(self):
        vec_start = Vector2()
        vec_end = Vector2()
        if self.dir == LEFT:
            vec_start = self.bot_left
            vec_end = self.top_left
        elif self.dir == RIGHT:
            vec_start = self.bot_right
            vec_end = self.top_right
        else:
            raise Exception

        vec_end.y += 2
        vec_end = vec_end.get_rotated_origin(vec_start, math.radians(30 * self.dir))

        t = 0.5
        inc_t = 1 / self.height
        result : list[Vector2] = []
        while t <= 1:
            position = vec_start.lerp(vec_end, t)
            result.append(position)
            t += inc_t

        return result

    def rotate_barrel(self, dest : Vector2):
        vDest = dest - self.barrel_pivot
        self.barrel_theta = Vector2.get_theta(Vector2.right(), vDest)
        if dest.y < self.barrel_pivot.y:
            self.barrel_theta *= -1
        prev_barrel_rect = self.update_barrel()
        map.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True)
        self.is_rect_invalid = True

    def fire(self):
        crnt_shell = shell.Shell("HP", self.barrel_position, self.barrel_theta)
        shell.add_shell(crnt_shell)


def stop_tank():
    if tank_player1:
        tank_player1.stop()

def move_tank(dir):
    if tank_player1:
        tank_player1.start_move(dir)

def send_mouse_pos(x, y):
    if tank_player1:
        tank_player1.rotate_barrel(Vector2(x, y))

def draw_debug():
    if tank_player1:
        # map.draw_debug_point(tank_player1.barrel_pivot)
        # map.draw_debug_point(tank_player1.get_rect().center)
        pass

def fire():
    if tank_player1:
        tank_player1.fire()

tank_player1 : Tank = None