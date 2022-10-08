import pico2d
from mytool import *
import map
        
class Tank(GroundObject):
    img_tank : pico2d.Image = None

    def __init__(self, center=(0,0)):
        global tank_player1

        if tank_player1:
            map.set_invalidate_rect(*tank_player1.get_rect().__getitem__())
            tank_player1 = None

        if Tank.img_tank == None:
            Tank.img_tank = load_image_path('tank_1.png')

        super().__init__(center, Tank.img_tank.w, Tank.img_tank.h)

        tank_player1 = None

    def set_pos(self, center):
        def dont_move(prev_theta, prev_center):
            self.set_theta(prev_theta)
            self.set_center(prev_center)

        from scene import screenHeight, screenWidth

        prev_rect = self.get_rect()
        prev_theta = self.rot_theta

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

        map.set_invalidate_rect(*prev_rect.__getitem__(), square=True)

        # if self.dir != 0:
        #     map.draw_debug_vectors(self.get_collision_vectors())
        return True

    def draw(self):
        self.draw_image(Tank.img_tank)

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True
        self.is_setting_mode = False

    def update(self):
        self.move()
        self.draw()


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
        

def draw_tanks():
    if tank_player1:
        tank_player1.draw()

def update():
    if tank_player1:
        tank_player1.move()

tank_player1 : Tank = None