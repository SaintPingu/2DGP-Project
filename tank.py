from math import fabs
import pico2d
import mytool
import map
import scene

class Tank:
    img_tank : pico2d.Image = None

    def __init__(self, center=(0,0)):
        global tank_player1

        if tank_player1:
            map.set_invalidate_rect(tank_player1.rect.center, tank_player1.rect.width, tank_player1.rect.height)
            tank_player1 = None

        self.prev_center = center
        if Tank.img_tank == None:
            Tank.img_tank = mytool.load_image_path('tank_1.png')
        self.rect = mytool.Rect(center, Tank.img_tank.w, Tank.img_tank.h)

        self.is_created = False
        self.dir = 0

        self.is_invalid_rect = False
        tank_player1 = None

    def attach_ground(self, dir_down=False):
        correction_height = 5

        result = map.get_highest_ground(self.rect, dir_down)

        if result == -1:
            return False
        dst_height = (result*map.CELL_SIZE)
        if self.is_created and dir_down == False:
            if dst_height > (self.rect.bottom + (self.rect.width//1.2)):
                return False

        self.rect.center = (self.rect.center[0], dst_height + correction_height)
        self.rect.update()

        return True

    def set_pos(self, center, invalidate=True, to_center=None):
        self.prev_center = self.rect.center
        self.rect.set_pos(center)

        if self.rect.left < 0:
            self.rect.center = (self.rect.width//2, self.rect.center[1])
            self.rect.update()
        elif self.rect.right >= scene.screenWidth:
            self.rect.center = (scene.screenWidth - self.rect.width//2, self.rect.center[1])
            self.rect.update()

        if invalidate:
            self.is_invalid_rect = True
            cell_x, cell_y = map.get_cell(center)
            if self.is_created or map.crnt_map[cell_y][cell_x] == map.BLOCK_PLACED_DIRT:
                is_attached = self.attach_ground(False)
                if not is_attached:
                    self.rect.set_pos(self.prev_center)
                    return False
            else:
                self.attach_ground(True)
            map.set_invalidate_rect(self.prev_center, self.rect.width, self.rect.height)

    def draw(self):
        if self.is_invalid_rect == False:
            return
        self.is_invalid_rect = False
        Tank.img_tank.draw(*self.rect.center)

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True

    def move(self):
        if self.dir == 0:
            return
        toX = 1 * self.dir
        
        to_center = (self.rect.center[0] + toX, self.rect.center[1])
        if to_center[1] > self.rect.center[1] + (self.rect.width//map.CELL_SIZE):
            return

        self.set_pos(to_center)
        #self.rotate()
    
    def start_move(self, dir):
        self.dir += dir

    def stop(self, dir):
        self.dir -= dir



        

        

def draw_tanks():
    if tank_player1:
        tank_player1.draw()

def update():
    if tank_player1:
        tank_player1.move()

tank_player1 : Tank = None