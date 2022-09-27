import pico2d
import mytool
import map
import scene
        
class Tank(mytool.GameObject):
    img_tank : pico2d.Image = None

    def __init__(self, center=(0,0)):
        global tank_player1

        if tank_player1:
            map.set_invalidate_rect(*tank_player1.get_rect().__getitem__())
            tank_player1 = None

        if Tank.img_tank == None:
            Tank.img_tank = mytool.load_image_path('tank_1.png')

        super().__init__(center, Tank.img_tank.w, Tank.img_tank.h)

        self.is_created = False
        self.speed = 0.5
        self.dir = 0
        self.vDir = mytool.Vector2()

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

    def move(self):
        if self.dir == 0:
            return
        elif self.dir == map.LEFT:
            self.vDir = self.get_vec_left()
        else:
            self.vDir = self.get_vec_right()

        vDest = mytool.Vector2(*self.center) + (self.vDir * self.speed)

        if self.set_pos(vDest) == False:
            self.stop()
    
    def update(self):
        self.move()
        self.draw()

    def start_move(self, dir):
        self.dir += dir

    def stop_dir(self, dir):
        if self.dir != 0:
            self.dir -= dir

    def stop(self):
        self.dir = 0
        

def draw_tanks():
    if tank_player1:
        tank_player1.draw()

def update():
    if tank_player1:
        tank_player1.move()

tank_player1 : Tank = None