import pico2d
from mytool import *
import map
import scene
        
class Tank(GameObject):
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
        prev_rect = self.get_rect()
        prev_theta = self.rot_theta

        self.set_center(center)
        if self.out_of_bound(0, scene.screenHeight, scene.screenWidth, 0):
            self.set_theta(prev_theta)
            self.set_center(prev_rect.center)
            return False

        if map.get_rotated_to_ground(self) == False:
            self.set_theta(prev_theta)
            self.set_center(prev_rect.center)
            return False

        map.set_invalidate_rect(*prev_rect.__getitem__(), square=True)

        return True

    def draw(self):
        self.draw_image(Tank.img_tank)
        # map.draw_debug_vectors(self.get_collision_vectors(LEFT))
        # map.draw_debug_vectors(self.get_collision_vectors(RIGHT))

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True
        self.is_setting_mode = False

    def update(self):
        self.move()
        self.draw()
        

def draw_tanks():
    if tank_player1:
        tank_player1.draw()

def update():
    if tank_player1:
        tank_player1.move()

tank_player1 : Tank = None