if __name__ == "__main__":
    quit()

from tools import *
import object
import gmap
import shell
import sprite
import gui
import sound
import framework
import state_inventory

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
    MAX_HP = 100
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
        self.hp = Tank.MAX_HP
        self.fuel = Tank.MAX_FUEL
        self.crnt_shell = "AP"
        self.is_locked = False
        self.is_sound_movement = False
        self.item_used = False
        self.item = None

        # gui
        self.gui_hp = gui.GUI_HP(self)
        self.gui_fuel = gui.GUI_Fuel(self, Tank.MAX_FUEL)
        gui.add_gui(self.gui_hp, 1)
        gui.add_gui(self.gui_fuel, 1)
    
    def release(self):
        if tank_list: # death
            tank_list.remove(self)
            gui.reset_degree()
            self.hp = 0
            self.gui_hp.invalidate()
        self.gui_hp.release()

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

    ##### Interactive #####
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

    def get_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            object.delete_object(self)
            sprite.add_animation("Tank_Explosion", self.center + (0,self.height//2))
            sound.play_sound('tank_explosion')
    
    def use_item(self, item_name):
        if self.item_used == True:
            return
        if item_name == "heal":
            self.item_used = True
            self.hp += 15
            self.hp = clamp(0, self.hp, Tank.MAX_HP)
            self.item = None
            gui.gui_weapon.set_item(None)
            gui.gui_weapon.set_image(self.crnt_shell)
        elif item_name == "TP":
            gui.gui_weapon.set_item(None)
        self.item = item_name

    ##### Movement #####
    def deselect(self):
        self.is_turn = False
        self.is_locked = False
        self.fuel = Tank.MAX_FUEL
        gui.reset_degree()
        
    def select(self):
        self.is_turn = True
        self.item = None
        self.item_used = False
        gui.gui_weapon.set_image(self.crnt_shell)
    
    def move(self):
        if super().move() == True:
            if self.is_sound_movement == False:
                self.is_sound_movement = True
                sound.play_sound('tank_movement', 64, channel=1, is_repeat=True)
    
    def stop(self):
        super().stop()
        sound.stop_sound('tank_movement')
        self.is_sound_movement = False

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
    
    def toggle_lock(self):
        if self.is_locked:
            if not gui_gauge.is_fill:
                crnt_tank.unlock()
        else:
            crnt_tank.lock()

    def fire(self):
        head = self.get_barrel_head()
        theta = self.get_barrel_theta()
        shell.add_shell(self.crnt_shell, head, theta, gui_gauge.get_filled(), self.item)
        self.dir = 0
        select_tank(None)
        sound.play_sound('tank_fire', 64)
    ##########




##### AI #####
class Tank_AI(Tank):
    START_UPDATE_DELAY = 1
    MAX_RUN_AI_SECOND = 0.3
    degree_table = {
        0 : 5,
        1 : 1.25,
        2 : 1.0,
        3 : 0.45,
        4 : 0.3,
        5 : 0.2,
        6 : 0.1,
        7 : 0.05,
    }
    error_table = {
        "easy" : 4,
        "normal" : 3,
        "hard" : 2,
        "god" : 0
    }
    error_range = 0
    def __init__(self, center=(0, 0)):
        super().__init__(center)
        self.init_values()
        self.is_checking = False
        self.is_moving = False
        self.shell_is_close = False
        self.count_update = 0

        self.max_movement_fuel = 0
        
        self.min_distance = float('inf')
        self.last_hit_degree = None
        self.result_degree = 0

        self.shell_selected = False
        self.power = 0
        self.degree_level = 0
        self.crnt_degree = 0
        self.start_degree = 0
        self.max_degree = 0
        self.update_delay = 0
        self.check_dir = None
        self.target_tank : Tank = None
        self.virtual_shell : shell.Shell = None
        self.item = None

        self.init_values()
    
    def init_values(self):
        self.is_checking = False

        self.min_distance = float('inf')
        self.last_hit_degree = None
        self.result_degree = 0

        self.shell_selected = False
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
        self.item = None
    
    def select(self):
        self.init_values()
        super().select()
        self.max_movement_fuel = 0
        self.target_tank = tank_list[0]
        self.set_movement()

    def set_movement(self):
        self.is_moving = random.randint(0, 5) > 0 # 5/6% chance to move
        if self.is_moving:
            if self.center.x < 100:
                self.dir = RIGHT
            elif self.center.x > SCREEN_WIDTH - 100:
                self.dir = LEFT
            else:
                self.dir = random.randrange(-1, 2, 2)

            self.max_movement_fuel = random.randint(0, Tank.MAX_FUEL - 20)

    def set_shell(self):
        REACHABLE_EVALUATION = 6
        distance = math.fabs(self.get_dx())

        avaliable_shells = ["AP"]
        shells = ["HP", "MUL", "NUCLEAR"]

        for s in shells:
            evaluation = (distance / shell.get_attributes(s)[0])
            # print(evaluation)
            if evaluation < REACHABLE_EVALUATION: # reachable
                avaliable_shells.append(s)
        
        if (distance / shell.get_attributes("MUL")[0]) < REACHABLE_EVALUATION / 3:
            avaliable_shells.append("MUL")

        
        shell_index = random.randint(0, len(avaliable_shells) - 1)
        self.crnt_shell = avaliable_shells[shell_index]
        self.shell_selected = True
        gui.gui_weapon.set_image(self.crnt_shell)

    def set_direction(self):
        self.check_dir = get_sign(self.get_dx())

        if self.check_dir == RIGHT:
            self.crnt_degree = self.get_rotation_degree() - 10
        else:
            self.crnt_degree = -self.get_rotation_degree() - 10
        self.max_degree = self.get_max_degree()

        self.precise_dir = 1
    
    def set_power(self):
        #distance = math.fabs(self.get_dx())
        pass

    def get_max_degree(self):
        degree = 90 - math.degrees(Vector2.get_theta(self.get_vec_right(), Vector2.up()))
        if self.check_dir == LEFT:
            degree *= -1 

        return 90 + Tank.MAX_DEGREE - degree + self.crnt_degree
    
    def get_dx(self):
        return self.target_tank.center.x - self.center.x


    def update(self):
        self.update_delay += framework.frame_time
        if self.update_delay >= Tank_AI.START_UPDATE_DELAY:
            if super().update() == False:
                return False

            self.run_ai()

    def fire(self):
        del self.virtual_shell
        self.virtual_shell = None

        self.crnt_degree = self.result_degree

        if Tank_AI.error_range != 0:
            error = (random.random() * 10) % Tank_AI.error_range - (Tank_AI.error_range/2)
            self.crnt_degree += error

        if self.check_dir == RIGHT:
            self.vec_dir_barrel = Vector2.right().get_rotated(math.radians(self.crnt_degree))
        else:
            self.vec_dir_barrel = Vector2.left().get_rotated(math.radians(-self.crnt_degree))

        self.set_barrel_pos()
        gui_gauge.set_fill(1)
        
        if self.item == None:
            self.item = random.randint(0, 1)
        state_inventory.set_window("item")
        framework.push_state(state_inventory)
        state_inventory.inventory.select(self.item)
        framework.pop_state()

        super().fire()
    
    def stop(self):
        super().stop()
        self.is_moving = False

    def run_ai(self):
        if self.is_moving:
            if self.fuel > self.max_movement_fuel:
                if self.move() == False:
                    self.stop()
            else:
                self.stop()
            return
        
        if self.shell_selected == False:
            self.set_shell()


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
            self.start_degree = self.crnt_degree

        # get impact point
        while self.count_update < Tank_AI.MAX_RUN_AI_SECOND:
            result = self.virtual_shell.update()
            # if self.degree_level >= 5:
            #     self.virtual_shell.draw()
            #     update_canvas()

            if result is not True:
                self.set_barrel_pos()
                vec_distance = self.virtual_shell.center - self.target_tank.center
                vec_distance.x = math.fabs(vec_distance.x)
                vec_distance.y = math.fabs(vec_distance.y)
                distance = vec_distance.get_norm()

                if type(result) == Tank: # tank on point
                    if distance < (self.detect_radius - 5): # n(==5) is correction value
                        self.result_degree = self.start_degree
                        self.fire()
                        return

                if distance < self.min_distance:
                    if (self.virtual_shell.center.x > 0 and self.virtual_shell.center.x < SCREEN_WIDTH): # in of screen
                        self.min_distance = distance
                        self.last_hit_degree = self.start_degree
                
                if vec_distance.y > 50 and (self.virtual_shell.center.x < 0 or self.virtual_shell.center.x > SCREEN_WIDTH): # out of screen
                    self.degree_level = 2
                elif vec_distance.x < 5:
                    # Find nearby hit point from hiding position if under the ground
                    if math.fabs(self.virtual_shell.vector.y) > math.fabs(self.virtual_shell.vector.x):
                        self.result_degree = self.start_degree
                        self.fire()
                        return
                elif vec_distance.x < 20:##
                   self.degree_level = 7
                elif vec_distance.x < 30:
                    self.degree_level = 6
                elif vec_distance.x < 60:
                    self.degree_level = 5
                elif vec_distance.x < 90:
                    self.degree_level = 4
                elif vec_distance.x < 120:
                    self.degree_level = 3
                elif vec_distance.x < 200:
                    self.degree_level = 2
                elif vec_distance.x < 300:
                    self.degree_level = 1
                else:
                    self.degree_level = 0
                
                self.crnt_degree += Tank_AI.degree_table[self.degree_level]

                if self.crnt_degree >= 90: # didn't find target tank
                    self.result_degree = self.last_hit_degree
                    self.fire()
                    return

                del self.virtual_shell
                self.virtual_shell = None
                break
            
            # NEED : not framework.frame_time
            self.count_update += framework.frame_time

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
            # NEED : draw
            if len(tank_list) == 1:
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
        
        from gui import gui_weapon
        gui_weapon.disable_item()

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



def handle_event(event):
    if not crnt_tank:
        return
    if type(crnt_tank) == Tank_AI:
        return

    if event.type == SDL_KEYDOWN:
        if event.key == SDLK_F1:
            gmap.start_draw_mode()
        elif event.key == SDLK_RIGHT:
            crnt_tank.start_move(RIGHT)
        elif event.key == SDLK_LEFT:
            crnt_tank.start_move(LEFT)
        elif event.key == SDLK_5: # for test
            crnt_tank.fuel = Tank.MAX_FUEL
        elif event.key == SDLK_F10:
            gui.toggle_gui()
        elif event.key == SDLK_F5:
            tank_list[0].get_damage(100)
            select_tank(None)
        elif event.key == SDLK_F6:
            tank_list[1].get_damage(100)
            select_tank(None)
        elif event.key == SDLK_SPACE:
            gui_gauge.fill(True)
    
    elif event.type == SDL_KEYUP:
        if event.key == SDLK_RIGHT or event.key == SDLK_LEFT:
            crnt_tank.stop()
        elif event.key == SDLK_SPACE:
            gui_gauge.fill(False)
            crnt_tank.fire()
            if framework.state_in_stack(state_inventory):
                framework.pop_state()
            
    elif event.type == SDL_MOUSEMOTION:
        mouse_pos = convert_pico2d(event.x, event.y)
        crnt_tank.update_barrel(Vector2(*mouse_pos))
        gui.set_degree(crnt_tank.center, math.degrees(crnt_tank.get_barrel_theta()))


    elif event.type == SDL_MOUSEBUTTONDOWN:
        mouse_pos = convert_pico2d(event.x, event.y)
        if event.button == SDL_BUTTON_LEFT:
            if point_in_rect(mouse_pos, gui.rect_gui):
                if point_in_rect(mouse_pos, gui.rect_weapon):
                    if not framework.state_in_stack(state_inventory):
                        state_inventory.set_window("weapon")
                        framework.push_state(state_inventory)
                        sound.play_sound('click')
                    else:
                        framework.pop_state()
                        sound.play_sound('click')
                        if state_inventory.get_window() == "item":
                            state_inventory.set_window("weapon")
                            framework.push_state(state_inventory)
                elif point_in_rect(mouse_pos, gui.rect_item):
                    if not framework.state_in_stack(state_inventory):
                        state_inventory.set_window("item")
                        framework.push_state(state_inventory)
                        sound.play_sound('click')
                    else:
                        framework.pop_state()
                        sound.play_sound('click')
                        if state_inventory.get_window() == "weapon":
                            state_inventory.set_window("item")
                            framework.push_state(state_inventory)
            else:
                crnt_tank.toggle_lock()



def set_shell(shell_name):
    if crnt_tank:
        crnt_tank.crnt_shell = shell_name
    
def set_item(item):
    if crnt_tank:
        if crnt_tank.item_used == False:
            crnt_tank.use_item(item[0])
            if item[0] == "heal":
                return
            if item[0] == "TP":
                gui.gui_weapon.set_image(item[0])
                return
            gui.gui_weapon.set_image(crnt_tank.crnt_shell)
            gui.gui_weapon.set_item(item[1])

def teleport(position):
    if prev_tank:
        gui.invalidate_degree()
        prev_tank.is_created = False
        prev_tank.set_pos(position)
        prev_tank.is_created = True

def apply_difficulty(difficulty):
    Tank_AI.error_range = Tank_AI.error_table[difficulty]
    


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