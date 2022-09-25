import pico2d
import math
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
        self.rot_theta = 0

        self.is_invalid_rect = False
        tank_player1 = None

    def attach_ground(self, dir_down=False):
        correction_height = 5

        result = map.get_highest_ground_rect(self.rect, dir_down)

        if result == -1:
            return False
        dst_height = (result*map.CELL_SIZE)

        if self.is_created and dir_down == False:
            if dst_height > (self.rect.bottom + (self.rect.width//1.2)):
                return False

        self.rect.center = (self.rect.center[0], dst_height + correction_height)
        self.rect.update()

        return True

    def set_pos(self, center, invalidate=True):
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
            center_cell_x, center_cell_y = map.get_cell(center)
            if self.is_created or map.is_block(map.crnt_map[center_cell_y][center_cell_x]):
                is_attached = self.attach_ground(False)
                if not is_attached:
                    self.rect.set_pos(self.prev_center)
                    return False
            else:
                self.attach_ground(True)

            self.rot_theta = map.get_theta_rotate_ground(self.rect)
            # if math.fabs(math.degrees(self.rot_theta)) == 90:
            #     point = map.get_highest_ground_point(self.rect.center[0], self.rect.bottom)
            #     if point:
            #         ground = map.get_pos_from_index(*point)
            #         self.rect.center = (self.rect.center[0], ground[1])
            #         self.rect.update()
            #         self.rot_theta = 0
            map.set_invalidate_rect(self.prev_center, self.rect.width, self.rect.height, square=True)

    def draw(self):
        if self.is_invalid_rect == False:
            return
        self.is_invalid_rect = False
        
        degree = math.fabs(math.degrees(self.rot_theta))
        if degree > 5:
            correction_y = 1
            if degree > 10:
                correction_y = 2
                if degree > 15:
                    correction_y = 4
                    if degree > 30:
                        correction_y = 6
                        if degree > 40:
                            correction_y = 8
                            if degree > 45:
                                correction_y = 10
            self.rect.center = (self.rect.center[0],self.rect.center[1] - correction_y)
            self.rect.update()

        print("self_degree : " + str(math.degrees(self.rot_theta)))
        Tank.img_tank.rotate_draw(self.rot_theta, *self.rect.center)

    def create(self):
        global tank_player1
        tank_player1 = self
        self.is_created = True

    def move(self):
        if self.dir == 0:
            return
        toX = 0.5 * self.dir
        
        to_center = (self.rect.center[0] + toX, self.rect.center[1])
        if to_center[1] > self.rect.center[1] + (self.rect.width//map.CELL_SIZE):
            return

        self.set_pos(to_center)
    
    def update(self):
        #self.theta = map.get_theta_rotate_ground(self.rect)
        self.move()


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