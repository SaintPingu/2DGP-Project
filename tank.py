from tools import *
from object import *
import gmap
import shell
import sprite

tank_green : Image = None
barrel_green : Image = None

def init():
    global tank_green, barrel_green
    tank_green = load_image_path('tank_green.png')
    barrel_green = load_image_path('barrel_green.png')

class Tank(GroundObject):
    def __init__(self, center=(0,0)):
        global tank_player1

        self.img_tank = tank_green
        self.img_barrel = barrel_green

        self.barrel_position = Vector2()
        self.barrel_pivot = Vector2()
        self.vec_dir_barrel = Vector2.right()
        self.hp = 100

        super().__init__(center, self.img_tank.w, self.img_tank.h)

        tank_player1 = None

    def set_pos(self, center):
        def dont_move(prev_theta, prev_center):
            self.set_theta(prev_theta)
            self.set_center(prev_center)

        prev_rect = self.get_rect()
        prev_theta = self.theta

        self.set_center(center)
        if self.out_of_bound(0, SCREEN_HEIGHT, SCREEN_WIDTH, 0):
            dont_move(prev_theta, prev_rect.center)
            return False

        # don't move if collision by the wall
        if self.dir != 0:
            vectors_coll = self.get_collision_vectors()
            for vector in vectors_coll:
                cell = get_cell(vector)
                block = get_block_cell(cell)
                if block is not False and is_block(block):
                    dont_move(prev_theta, prev_rect.center)
                    return False

        
        if self.rotate_ground() == False:
            dont_move(prev_theta, prev_rect.center)
            return False
        
        self.rotate_barrel()
        # invalidate
        prev_barrel_rect = self.update_barrel()
        gmap.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True)
        gmap.set_invalidate_rect(*prev_rect.__getitem__(), square=True)
        self.is_rect_invalid = True

        return True

    def invalidate(self):
        gmap.set_invalidate_rect(self.barrel_position, self.img_barrel.w, self.img_barrel.h, square=True)
        gmap.set_invalidate_rect(*self.get_rect().__getitem__(), square=True)
        self.is_rect_invalid = True

    def draw(self):
        if self.is_rect_invalid == False:
            return

        theta = self.get_barrel_theta()
        self.img_barrel.rotate_draw(theta, *self.barrel_position)
        self.draw_image(self.img_tank)

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True
        self.is_setting_mode = False

    def update(self):
        self.move()

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

    ##### Barrel #####
    def get_barrel_head(self):
        return self.barrel_position + (self.vec_dir_barrel * self.img_barrel.w/2)
    def get_barrel_theta(self):
        if self.vec_dir_barrel.y > 0:
            return Vector2.right().get_theta(self.vec_dir_barrel)
        else:
            return -Vector2.right().get_theta(self.vec_dir_barrel)

    def update_barrel(self):
        prev_barrel_rect = Rect(self.barrel_position, self.img_barrel.w, self.img_barrel.h)
        vec_normal = self.get_vec_right().get_rotated(math.pi/2)
        self.barrel_pivot = self.center + (vec_normal * 3)
        self.barrel_position = self.barrel_pivot + self.vec_dir_barrel * (self.img_barrel.w/2)
        # gmap.draw_debug_vector(self.barrel_pivot)
        # gmap.draw_debug_vector(self.center)
        return prev_barrel_rect

    def rotate_barrel(self, target : Vector2 = None):
        if target is None:
            target = self.get_barrel_head()
        self.vec_dir_barrel = self.vec_dir_barrel.get_rotated_dest(self.barrel_pivot, target)

        # 180 degree rotation
        if self.vec_dir_barrel.x < 0:
            left_dir = self.get_vec_left().get_rotated(math.radians(10))
            if self.vec_dir_barrel.y <= left_dir.y:
                self.vec_dir_barrel = left_dir
        else:
            right_dir = self.get_vec_right().get_rotated(math.radians(-10))
            if self.vec_dir_barrel.y <= right_dir.y:
                self.vec_dir_barrel = right_dir

        prev_barrel_rect = self.update_barrel()
        gmap.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True)
        self.is_rect_invalid = True
    ##########

    def fire(self):
        head = self.get_barrel_head()
        theta = self.get_barrel_theta()
        crnt_shell = shell.Shell("HP", self.barrel_pivot, theta)
        #crnt_shell = shell.Shell("AP", self.barrel_position, self.barrel_theta)
        shell.add_shell(crnt_shell)
        # crnt_shell = shell.Shell("MUL", self.barrel_position, self.barrel_theta)
        # shell.add_shell(crnt_shell)
        # crnt_shell = shell.Shell("MUL", self.barrel_position, self.barrel_theta - 0.02)
        # shell.add_shell(crnt_shell)
        # crnt_shell = shell.Shell("MUL", self.barrel_position, self.barrel_theta + 0.02)
        # shell.add_shell(crnt_shell)
        # crnt_shell = shell.Shell("MUL", self.barrel_position, self.barrel_theta - 0.04)
        # shell.add_shell(crnt_shell)
        # crnt_shell = shell.Shell("MUL", self.barrel_position, self.barrel_theta + 0.04)
        # shell.add_shell(crnt_shell)

        sprite.add_animation("Shot", head, theta=theta, parent=self)


def check_invalidate(position, radius):
    if tank_player1:
        if tank_player1.is_in_radius(position, radius):
            tank_player1.is_rect_invalid = True

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
        pass

def fire():
    if tank_player1:
        tank_player1.fire()

tank_player1 : Tank = None