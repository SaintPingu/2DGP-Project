from tools import *
import object
import gmap
import shell
import sprite
import gui

image_tank_green : Image = None
image_barrel_green : Image = None
image_tank_blue : Image = None
image_barrel_blue : Image = None
image_tank_red : Image = None
image_barrel_red : Image = None

gui_selection : gui.GUI_Select_Tank = None

def enter():
    global image_tank_green, image_barrel_green, image_tank_blue, image_barrel_blue, image_tank_red, image_barrel_red
    image_tank_green = load_image_path('tank_green.png')
    image_barrel_green = load_image_path('barrel_green.png')
    image_tank_blue = load_image_path('tank_blue.png')
    image_barrel_blue = load_image_path('barrel_blue.png')
    image_tank_red = load_image_path('tank_red.png')
    image_barrel_red = load_image_path('barrel_red.png')

    global gui_selection
    selection_arrow = load_image_path('selection_arrow.png')
    gui_selection = gui.GUI_Select_Tank(selection_arrow)
    gui.add_gui(gui_selection)

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
    gui_selection = None

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
        _wait_count += 1
        if _wait_count > 60:
            select_next_tank()
            gmap.env.wind.randomize()
            _wait_count = 0
        

class Tank(object.GroundObject):
    def __init__(self, center=(0,0)):
        self.image = image_tank_green
        self.image_barrel = image_barrel_green

        self.barrel_position = Vector2()
        self.barrel_pivot = Vector2()
        self.vec_dir_barrel = Vector2.right()

        self.index = 0
        self.team = "green"
        self.hp = 100
        self.crnt_shell = "AP"

        super().__init__(center, self.image.w, self.image.h)
        self.gui_hp = gui.GUI_HP(self)
        gui.add_gui(self.gui_hp)
    
    def release(self):
        if tank_list:
            tank_list.remove(self)
        gui.del_gui(self.gui_hp)

    def set_team(self, team : str):
        self.team = team
        if team == "green":
            self.image = image_tank_green
            self.image_barrel = image_barrel_green
        elif team == "blue":
            self.image = image_tank_blue
            self.image_barrel = image_barrel_blue
        elif team == "red" or team == 'ai':
            self.image = image_tank_red
            self.image_barrel = image_barrel_red
        else:
            assert False


    def invalidate(self):
        gmap.set_invalidate_rect(self.barrel_position, self.image_barrel.w, self.image_barrel.h, square=True, grid_size=0)
        gmap.set_invalidate_rect(*self.get_rect().__getitem__(), square=True)
        self.gui_hp.invalidatae()
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
        self.move()
        self.update_barrel()

    ##### Movement #####
    def set_pos(self, center):
        def dont_move(prev_theta, prev_center):
            self.set_theta(prev_theta)
            self.set_center(prev_center)

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

        return True

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

        vec_end = vec_end.get_rotated_origin(vec_start, math.radians(30 * dir))

        t = 0.5
        inc_t = 1 / self.height
        result : list[Vector2] = []
        while t <= 1:
            position = vec_start.lerp(vec_end, t)
            result.append(position)
            t += inc_t

        return result
    
    def get_collision_cells(self):
        collision_vectors : list[Vector2] = []
        collision_vectors.extend(self.get_vectors_bot())
        collision_vectors.extend(self.get_vectors_top(0.2))
        collision_vectors.extend(self.get_side_vectors(LEFT))
        collision_vectors.extend(self.get_side_vectors(RIGHT))

        result_cells : set[Vector2] = set()
        for vector in collision_vectors:
            result_cells.add(gmap.get_cell(vector))

        return result_cells

    def check_collision(self, position : Vector2, radius):
        collision_cells = self.get_collision_cells()
        for cell in collision_cells:
            cell_pos = Vector2(*gmap.get_pos_from_cell(*cell))
            distance = (cell_pos - position).get_norm()
            if distance <= gmap.CELL_SIZE//2 + radius:
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
        if is_debug_mode():
            gmap.draw_debug_vector(self.barrel_pivot)
            gmap.draw_debug_vector(self.center)
        return prev_barrel_rect

    def update_barrel(self, target : Vector2 = None):
        if target is None:
            target = self.get_barrel_head()
        self.vec_dir_barrel = self.vec_dir_barrel.get_rotated_dest(self.barrel_pivot, target)

        # 190 degree rotation
        if self.vec_dir_barrel.x < 0:
            left_dir = self.get_vec_left().get_rotated(math.radians(10))
            if self.vec_dir_barrel.y <= left_dir.y:
                self.vec_dir_barrel = left_dir
        else:
            right_dir = self.get_vec_right().get_rotated(math.radians(-10))
            if self.vec_dir_barrel.y <= right_dir.y:
                self.vec_dir_barrel = right_dir

        prev_barrel_rect = self.set_barrel_pos()
        gmap.set_invalidate_rect(*prev_barrel_rect.__getitem__(), square=True, grid_size=0)
        self.is_rect_invalid = True

    ##### Shell #####
    def select_shell(self, shell_name):
        self.crnt_shell = shell_name

    def fire(self):
        head = self.get_barrel_head()
        theta = self.get_barrel_theta()
        shell.add_shell(self.crnt_shell, head, theta)
        sprite.add_animation("Shot", head, theta=theta, parent=self)
        select_tank(None)
    ##########
    def get_damage(self, damage):
        self.gui_hp.invalidatae()
        self.gui_hp.update_gauge()
        self.hp -= damage

tank_list : list[Tank]
crnt_tank : Tank = None
crnt_index = 0

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
    global crnt_tank, gui_selection
    crnt_tank = tank
    gui_selection.set_owner(crnt_tank)

def select_next_tank():
    global tank_list, crnt_tank, crnt_index
    crnt_index += 1
    if crnt_index >= len(tank_list):
        crnt_index = 0
    
    if len(tank_list) > 0:
        crnt_tank = tank_list[crnt_index]
        select_tank(crnt_tank)
    

def check_invalidate(position, radius):
    for tank in tank_list:
        if tank.is_in_radius(position, radius):
            tank.is_rect_invalid = True

def check_hit(position : Vector2, radius, damage):
    for tank in tank_list:
        if tank.is_in_radius(position, radius):
            if tank.check_collision(position, radius):
                tank.get_damage(damage)
                return tank.center
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
        crnt_tank.update_barrel(Vector2(x, y))

def draw_debug():
    if crnt_tank:
        pass

def fire():
    if crnt_tank:
        crnt_tank.fire()


def read_data(file):
    file.readline()

    while True:
        data = file.readline()
        if data == END_OF_LINE:
            if len(tank_list) > 0:
                select_tank(tank_list[0])
            return

        tank = Tank()
        values = data.split()
        tank.index = int(values[0])
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