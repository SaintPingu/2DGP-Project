if __name__ == "__main__":
    quit()

from tools import *
import object
import gmap
import shell
import sprite
import gui
import framework
import environment as env

image_tank_green : Image
image_barrel_green : Image
image_tank_blue : Image
image_barrel_blue : Image
image_tank_red : Image
image_barrel_red : Image

gui_selection : gui.GUI_Select_Tank
gui_launch : gui.GUI_LAUNCH
gui_gauge : gui.GUI_GUAGE


TANK_SPEED_KMPH = 30
TANK_SPEED_MPM = (TANK_SPEED_KMPH * 1000.0 / 60.0)
TANK_SPEED_MPS = (TANK_SPEED_MPM / 60.0)
TANK_SPEED_PPS = (TANK_SPEED_MPS * PIXEL_PER_METER)
        

class Tank(object.GroundObject):
    MAX_DEGREE = 10
    MAX_FUEL = TANK_SPEED_KMPH * 5
    def __init__(self, center=(0,0)):
        self.image = image_tank_green
        self.image_barrel = image_barrel_green
        super().__init__(center, self.image.w, self.image.h)

        self.barrel_position = Vector2()
        self.barrel_pivot = Vector2()
        self.vec_dir_barrel = Vector2.right()

        # tank
        self.is_turn = False
        self.index = 0
        self.team = "green"

        # attributes
        self.speed = TANK_SPEED_PPS
        self.hp = 100
        self.fuel = Tank.MAX_FUEL
        self.crnt_shell = "AP"
        self.is_locked = False

        # gui
        self.gui_hp = gui.GUI_HP(self)
        self.gui_fuel = gui.GUI_Fuel(self, Tank.MAX_FUEL)
        gui.add_gui(self.gui_hp, 1)
        gui.add_gui(self.gui_fuel, 1)
    
    def release(self):
        if tank_list:
            tank_list.remove(self)
        self.gui_hp.release()

    def set_team(self, team : str):
        self.team = team
        if team == "green":
            self.image = image_tank_green
            self.image_barrel = image_barrel_green
        elif team == "blue":
            self.image = image_tank_blue
            self.image_barrel = image_barrel_blue
        elif team == "red":
            self.image = image_tank_red
            self.image_barrel = image_barrel_red
        else:
            assert False


    def invalidate(self):
        gmap.set_invalidate_rect(self.barrel_position, self.image_barrel.w, self.image_barrel.h, square=True, grid_size=0)
        gmap.set_invalidate_rect(*self.get_rect().__getitem__(), square=True)
        self.gui_hp.invalidate()
        self.is_rect_invalid = True

    def draw(self):
        if self.is_rect_invalid == False:
            return
        self.is_rect_invalid = True

        theta = self.get_barrel_theta()
        self.image_barrel.rotate_draw(theta, *self.barrel_position)
        self.image.rotate_draw(self.theta, *self.center)

    def create(self):
        self.is_created = True

    def update(self):
        self.update_barrel()
        if crnt_tank != self:
            return False

        self.move()

        if is_debug_mode():
            gmap.draw_debug_cells(self.get_collision_cells())

    def get_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            object.delete_object(self)
            sprite.add_animation("Tank_Explosion", self.center + (0,self.height//2))

    ##### Movement #####
    def deselect(self):
        self.is_turn = False
        self.is_locked = False
        self.fuel = Tank.MAX_FUEL
        
    def select(self):
        self.is_turn = True
        gui.gui_weapon.set_image(self.crnt_shell)

    def set_pos(self, center):
        def dont_move(prev_theta, prev_center):
            self.set_theta(prev_theta)
            self.set_center(prev_center)

        if self.is_created and self.fuel <= 0:
            return False
            
        prev_rect = self.get_rect()
        prev_theta = self.theta

        self.set_center(center)
        if self.out_of_bound(0, SCREEN_HEIGHT, SCREEN_WIDTH, MIN_HEIGHT):
            dont_move(prev_theta, prev_rect.center)
            return False

        # don't move if collision by the wall
        if self.dir != 0:
            vectors_coll = self.get_side_vectors()
            for vector in vectors_coll:
                cell = gmap.get_cell(vector)
                if gmap.get_block_cell(cell):
                    dont_move(prev_theta, prev_rect.center)
                    return False
            if is_debug_mode():
                #gmap.draw_debug_vectors(vectors_coll)
                pass
        
        if self.rotate_ground() == False:
            dont_move(prev_theta, prev_rect.center)
            return False
        
        # invalidate
        prev_barrel_rect = self.set_barrel_pos()
        gmap.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True, grid_size=0)
        gmap.set_invalidate_rect(*prev_rect.__getitem__(), square=True)
        self.is_rect_invalid = True

        self.fuel -= 1

        return True
    
    def get_rotation_degree(self):
        theta = Vector2.right().get_theta(self.get_vec_right())
        return math.degrees(theta)

    ##### Collision #####
    def get_side_vectors(self, dir=None):
        vec_start = Vector2()
        vec_end = Vector2()

        if dir is None:
            dir = self.dir

        if dir == LEFT:
            vec_start = self.bot_left
            vec_end = self.top_left
        elif dir == RIGHT:
            vec_start = self.bot_right
            vec_end = self.top_right
        else:
            assert False

        vec_end = vec_end.get_rotated_pivot(vec_start, math.radians(30 * dir))

        return gmap.get_vectors(vec_start, vec_end, 0.5)

    def get_collision_cells(self):
        collision_vectors : list[Vector2] = []
        collision_vectors.extend(self.get_vectors_bot())
        collision_vectors.extend(self.get_vectors_top(0.3, 0.7))
        collision_vectors.extend(self.get_side_vectors(LEFT))
        collision_vectors.extend(self.get_side_vectors(RIGHT))

        result_cells : set[Vector2] = set()
        for vector in collision_vectors:
            result_cells.add(gmap.get_cell(vector))

        return result_cells

    def check_collision(self, vectors : list[Vector2]):
        collision_cells = self.get_collision_cells()

        target_cells : set[Vector2] = set()
        for vector in vectors:
            target_cells.add(gmap.get_cell(vector))

        if len(collision_cells & target_cells) > 0:
                return True
        return False

    ##### Barrel #####
    def get_barrel_head(self):
        return self.barrel_position + (self.vec_dir_barrel * self.image_barrel.w/2)
    def get_barrel_theta(self):
        if self.vec_dir_barrel.y > 0:
            return Vector2.right().get_theta(self.vec_dir_barrel)
        else:
            return -Vector2.right().get_theta(self.vec_dir_barrel)

    def set_barrel_pos(self):
        prev_barrel_rect = Rect(self.barrel_position, self.image_barrel.w, self.image_barrel.h)
        vec_normal = self.get_normal()
        self.barrel_pivot = self.center + (vec_normal * 3)
        self.barrel_position = self.barrel_pivot + self.vec_dir_barrel * (self.image_barrel.w/2)
        # if is_debug_mode():
        #     gmap.draw_debug_vector(self.barrel_pivot)
        #     gmap.draw_debug_vector(self.center)
        return prev_barrel_rect

    def update_barrel(self, target : Vector2 = None):
        if self.is_locked == False:
            if target is None:
                target = self.get_barrel_head()
            self.vec_dir_barrel = self.vec_dir_barrel.get_rotated_dest(self.barrel_pivot, target)

            # 190 degree rotation
            if self.vec_dir_barrel.x < 0:
                left_dir = self.get_vec_left().get_rotated(math.radians(Tank.MAX_DEGREE))
                if self.vec_dir_barrel.y <= left_dir.y:
                    self.vec_dir_barrel = left_dir
            else:
                right_dir = self.get_vec_right().get_rotated(math.radians(-Tank.MAX_DEGREE))
                if self.vec_dir_barrel.y <= right_dir.y:
                    self.vec_dir_barrel = right_dir

        prev_barrel_rect = self.set_barrel_pos()
        gmap.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True, grid_size=0)
        self.is_rect_invalid = True

    ##### Shell #####
    def select_shell(self, shell_name):
        self.crnt_shell = shell_name

    def lock(self):
        self.is_locked = True
        gui_launch.set_state('fire')
    
    def unlock(self):
        self.is_locked = False
        gui_launch.set_state('locked')

    def fire(self):
        head = self.get_barrel_head()
        theta = self.get_barrel_theta()
        shell.add_shell(self.crnt_shell, head, theta, gui_gauge.get_filled())
        sprite.add_animation("Shot", head, theta=theta)
        self.dir = 0
        select_tank(None)
    ##########




##### AI #####
class Tank_AI(Tank):
    START_UPDATE_DELAY = 120
    MAX_CHECK_COUNT = 30
    degree_table = {
        0 : 5,
        1 : 1.5,
        2 : 1.2,
        3 : 0.6,
        4 : 0.3,
        5 : 0.2,
        6 : 0.1,
    }
    def __init__(self, center=(0, 0)):
        super().__init__(center)
        self.init_values()
        self.is_checking = False
        self.is_moving = False
        self.shell_is_close = False
        self.count_update = 0
        self.min_distance = float('inf')
        self.result_vector : Vector2 = None

        self.max_movement_fuel = 0
        
        self.last_hit_vector : Vector2 = None
        self.last_hit_distance = float('inf')

        self.power = 0
        self.degree_level = 0
        self.crnt_degree = 0
        self.start_degree = 0
        self.max_degree = 0
        self.update_delay = 0
        self.check_dir = None
        self.target_tank : Tank = None
        self.virtual_shell : shell.Shell = None

        self.init_values()
    
    def select(self):
        super().select()
        self.max_movement_fuel = 0
        self.target_tank = tank_list[0]
        self.set_movement()

    def set_movement(self):
        dx = self.get_dx()
        distance = math.fabs(dx)

        shell_speed = shell.get_attributes(self.crnt_shell)[0]
        env.wind.get_wind_vector()
        evaluation = (distance / shell_speed)

        if evaluation > 70: # can't reach
            self.is_moving = True
            self.dir = get_sign(dx)
            self.max_movement_fuel = 0
        else:
            self.is_moving = random.randint(0, 5) > 0 # 5/6% chance to move
            if self.is_moving:
                if self.center.x < 100:
                    self.dir = RIGHT
                elif self.center.x > SCREEN_WIDTH - 100:
                    self.dir = LEFT
                else:
                    self.dir = random.randrange(-1, 2, 2)

            self.max_movement_fuel = random.randint(0, Tank.MAX_FUEL - 20)

    def init_values(self):
        self.is_checking = False
        self.min_distance = float('inf')
        self.result_vector = None

        self.last_hit_vector = None
        self.last_hit_distance = float('inf')

        self.power = 0
        self.degree_level = 0
        self.count_update = 0
        self.start_degree = 0
        self.crnt_degree = 0
        self.max_degree = 0
        self.update_delay = 0
        self.check_dir = None
        self.precise_dir = None
        self.target_tank = None
        self.virtual_shell = None

    def set_direction(self):
        self.check_dir = get_sign(self.get_dx())

        if self.check_dir == RIGHT:
            self.crnt_degree = self.get_rotation_degree() - 10
        else:
            self.crnt_degree = -self.get_rotation_degree() - 10
        self.max_degree = self.get_max_degree()

        self.precise_dir = 1
    
    def set_power(self):
        distance = math.fabs(self.get_dx())

    def get_max_degree(self):
        degree = 90 - math.degrees(Vector2.get_theta(self.get_vec_right(), Vector2.up()))
        if self.check_dir == LEFT:
            degree *= -1 

        return 90 + Tank.MAX_DEGREE - degree + self.crnt_degree
    
    def get_dx(self):
        return self.target_tank.center.x - self.center.x


    def update(self):
        self.update_delay += 1
        if self.update_delay >= Tank_AI.START_UPDATE_DELAY:
            if super().update() == False:
                return False

            self.run_ai()

    def fire(self):
        del self.virtual_shell
        self.virtual_shell = None

        self.set_barrel_pos()
        gui_gauge.set_fill(1)
        super().fire()
        self.init_values()
    
    def stop(self):
        self.dir = 0
        self.is_moving = False

    def run_ai(self):
        if self.is_moving:
            if self.fuel > self.max_movement_fuel:
                if self.move() == False:
                    self.stop()
            else:
                self.stop()
            return

        if self.is_checking == False:
            self.is_checking = True

            if self.check_dir == None:
                self.set_power()
                self.set_direction()

            # create virtual shell
            if self.check_dir == RIGHT:
                self.vec_dir_barrel = Vector2.right().get_rotated(math.radians(self.crnt_degree))
            else:
                self.vec_dir_barrel = Vector2.left().get_rotated(math.radians(-self.crnt_degree))
                
            self.virtual_shell = shell.Shell(self.crnt_shell, self.get_barrel_head(), self.get_barrel_theta(), is_simulation=True)
            self.start_barrel_vec = self.vec_dir_barrel

        # get impact point
        while self.count_update < Tank_AI.MAX_CHECK_COUNT:
            result = self.virtual_shell.update()
            # if self.degree_level >= 5:
            #     self.virtual_shell.draw()
            #     update_canvas()

            if result is not True:
                self.set_barrel_pos()
                distance = math.fabs(self.virtual_shell.center.x - self.target_tank.center.x)

                if type(result) == Tank: # tank on point
                    if distance < self.last_hit_distance:
                        self.last_hit_vector = Vector2(*self.vec_dir_barrel)
                        self.last_hit_distance = distance
                
                if distance < self.min_distance:
                    self.min_distance = distance
                    self.result_vector = Vector2(*self.vec_dir_barrel)
                
                self.shell_is_close = False
                if distance < 8:
                    # Find nearby hit point from hiding position if under the ground
                    if self.last_hit_vector is None:
                        if math.fabs(self.virtual_shell.vector.y) > math.fabs(self.virtual_shell.vector.x):
                            self.fire()
                            return
                        self.degree_level = 0
                    else:
                        self.vec_dir_barrel = self.start_barrel_vec
                        self.fire()
                        return
                elif distance < 20:
                    if math.fabs(self.virtual_shell.vector.x) > math.fabs(self.virtual_shell.center.y):
                        if self.last_hit_vector:
                            self.fire()
                            return
                elif distance < 30:
                    self.degree_level = 6
                elif distance < 60:
                    self.degree_level = 5
                elif distance < 90:
                    self.degree_level = 4
                elif distance < 120:
                    self.degree_level = 3
                elif distance < 200:
                    self.degree_level = 2
                elif distance < 300:
                    self.degree_level = 1
                else:
                    self.degree_level = 0
                
                self.crnt_degree += Tank_AI.degree_table[self.degree_level]

                if self.crnt_degree >= 90: # tank is hided under ground
                    if self.last_hit_vector:
                        self.vec_dir_barrel = self.last_hit_vector
                    else:
                        self.vec_dir_barrel = self.result_vector
                    self.update_barrel()
                    self.fire()
                    return

                del self.virtual_shell
                self.virtual_shell = None
                break
            self.count_update += 1

        self.count_update = 0
        if self.virtual_shell is None:
            self.is_checking = False
        


tank_list : list[Tank]
crnt_tank : Tank = None
prev_tank : Tank = None
crnt_index = 0

def enter():
    global image_tank_green, image_barrel_green, image_tank_blue, image_barrel_blue, image_tank_red, image_barrel_red
    image_tank_green = load_image_path('tank_green.png')
    image_barrel_green = load_image_path('barrel_green.png')
    image_tank_blue = load_image_path('tank_blue.png')
    image_barrel_blue = load_image_path('barrel_blue.png')
    image_tank_red = load_image_path('tank_red.png')
    image_barrel_red = load_image_path('barrel_red.png')

    global gui_selection, gui_launch, gui_gauge
    selection_arrow = load_image_path('selection_arrow.png')
    gui_selection = gui.GUI_Select_Tank(selection_arrow)
    gui_launch = gui.GUI_LAUNCH()
    gui_gauge = gui.GUI_GUAGE()
    gui.add_gui(gui_selection, 1)
    gui.add_gui(gui_launch, 1)
    gui.add_gui(gui_gauge, 1)

    global tank_list, crnt_index
    tank_list = []
    crnt_index = 0

def exit():
    global  image_tank_green, image_barrel_green, image_tank_blue, image_barrel_blue, image_tank_red, image_barrel_red, gui_selection
    del image_tank_green
    del image_barrel_green
    del image_tank_blue
    del image_barrel_blue
    del image_tank_red
    del image_barrel_red

    global tank_list, crnt_tank, _wait_count
    tank_list.clear()
    del tank_list
    tank_list = None

    crnt_tank = None
    _wait_count = 0

_wait_count = 0
def update():
    global _wait_count
    if crnt_tank is None and len(shell.fired_shells) <= 0:
        _wait_count += framework.frame_time
        if _wait_count > 2:
            if len(tank_list) <= 1:
                if type(tank_list[0]) == Tank_AI:
                    return -1
                return 0
            select_next_tank()
            gmap.env.wind.randomize()
            _wait_count = 0
    
    return True










def new_tank():
    tank = Tank()
    tank.index = len(tank_list)
    tank_list.append(tank)
    object.add_object(tank)

    return tank

def add_tank(tank):
    tank_list.append(tank)
    object.add_object(tank)

def select_tank(tank):
    global prev_tank, crnt_tank, gui_selection

    if crnt_tank is not None:
        prev_tank = crnt_tank

    crnt_tank = tank
    
    if crnt_tank is not None:
        if prev_tank:
            prev_tank.deselect()
        crnt_tank.select()
        gui_gauge.reset()

    gui_selection.set_owner(crnt_tank)

def select_next_tank():
    gui_launch.set_state('locked')

    global tank_list, crnt_index
    crnt_index += 1
    if crnt_index >= len(tank_list):
        crnt_index = 0
    
    if len(tank_list) > 0:
        tank = tank_list[crnt_index]
        select_tank(tank)
    

def check_invalidate(position, radius):
    for tank in tank_list:
        if tank.is_in_radius(position, radius):
            tank.is_rect_invalid = True

def check_hit(position : Vector2, collision_vectors, radius, damage):
    for tank in tank_list:
        if tank.is_in_radius(position, radius):
            if tank.check_collision(collision_vectors):
                tank.get_damage(damage)
                return tank
    return False


def check_explosion(position : Vector2, radius, damage):
    for tank in tank_list:
        if tank.is_in_radius(position, radius):
            tank.get_damage(damage)

def stop_tank():
    if crnt_tank:
        crnt_tank.stop()

def move_tank(dir):
    if crnt_tank:
        crnt_tank.start_move(dir)

def send_mouse_pos(x, y):
    if crnt_tank:
        if type(crnt_tank) != Tank_AI:
            crnt_tank.update_barrel(Vector2(x, y))

def draw_debug():
    if crnt_tank:
        pass

def toggle_lock():
    if crnt_tank:
        if crnt_tank.is_locked:
            if not gui_gauge.is_fill:
                crnt_tank.unlock()
        else:
            crnt_tank.lock()


def fill_gauge():
    if crnt_tank:
        if crnt_tank.is_locked:
            gui_gauge.fill(True)
    
def stop_gauge():
    if crnt_tank:
        if crnt_tank.is_locked:
            gui_gauge.fill(False)
            crnt_tank.fire()

def fire():
    if crnt_tank:
        crnt_tank.fire()

def set_shell(shell_name):
    if crnt_tank:
        crnt_tank.crnt_shell = shell_name


def read_data(file, mode):
    file.readline()

    while True:
        data = file.readline()
        if data == END_OF_LINE:
            if len(tank_list) > 0:
                select_tank(tank_list[0])
            return

        values = data.split()
        index = int(values[0])

        if mode == "PVE" and index == 1:
            tank = Tank_AI()
        else:
            tank = Tank()
        
        tank.index = index
        tank.set_team(values[1])
        tank.hp = int(values[2])
        tank.center.x = float(values[3])
        tank.center.y = float(values[4])
        tank.theta = float(values[5])
        tank.update_object()
        tank.create()

        add_tank(tank)

def write_data(file):
    file.write('[ tank list ]\n')
    for tank in tank_list:
        if tank.is_created == False:
            continue
        file.write(str(tank.index) + ' ')
        file.write(str(tank.team) + ' ')
        file.write(str(tank.hp) + ' ')
        file.write(str(tank.center.x) + ' ')
        file.write(str(tank.center.y) + ' ')
        file.write(str(tank.theta) + ' ')
        file.write('\n')
    file.write(END_OF_LINE)