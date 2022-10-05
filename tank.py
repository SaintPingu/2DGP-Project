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

        self.is_created = False
        self.speed = 2
        self.dir = 0
        self.vDir = Vector2()

        tank_player1 = None

    def set_pos(self, center):
        rect = self.get_rect()

        self.set_center(center)
        if self.out_of_bound(0, scene.screenHeight, scene.screenWidth, 0):
            self.set_center(rect.center)
            return False

        self = map.get_rotated_to_ground(self)
        map.set_invalidate_rect(*rect.__getitem__(), square=True)

        return True

    def draw(self):
        self.draw_image(Tank.img_tank)
        #map.draw_debug_vectors(self.get_vectors_bot())

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True

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