from tools import *
import object
import gmap
import sprite
import tank


SHELLS = {}

def enter():
    global SHELLS
    img_shell_ap = load_image_path('shell_ap.png')
    img_shell_hp = load_image_path('shell_hp.png')
    img_shell_mul = load_image_path('shell_multiple.png')
    SHELLS = { "AP" : img_shell_ap, "HP" : img_shell_hp, "MUL" : img_shell_mul }

def exit():
    global SHELLS
    for image in SHELLS.values():
        del image


class Shell(object.GameObject):
    def __init__(self, shell_name : str, position, theta):
        assert shell_name in SHELLS.keys()

        self.img_shell : Image = SHELLS[shell_name]
        super().__init__(position, self.img_shell.w, self.img_shell.h, theta)

        self.vector = Vector2.right().get_rotated(theta)
        self.speed, self.damage, self.explosion_radius = get_attributes(shell_name)
        self.temp = None
        self.is_destroyed = False

    def draw(self):
        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
        if self.temp:
            gmap.draw_debug_point(self.temp)
    
    def move(self):
        dest = (self.center + self.vector * self.speed) + gmap.env.wind.get_wind_vector()
        self.vector = self.vector.get_rotated_dest(self.center, dest)
        self.set_center(dest)

    def update(self):
        self.invalidate()
        rect = self.get_squre()

        # out of range
        if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.top <= MIN_HEIGHT:
            delete_shell(self)
            return
        
        self.move()

        head = self.get_head()
        rect_detection = Rect(head, 4, 4)
        detected_cells = gmap.get_detected_cells(rect_detection)
        for detected_cell in detected_cells:
            if not gmap.out_of_range_cell(*detected_cell) and gmap.get_block_cell(detected_cell):
                self.explosion(head)
                self.invalidate()
                delete_shell(self)
                return
        if is_debug_mode():
            gmap.draw_debug_rect(rect_detection)

        self.is_rect_invalid = True

        # apply rotation and gravity
        self.vector = self.vector.lerp(Vector2.down(), 0.006)
        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y < 0:
            self.speed += 0.05
            self.theta *= -1

    def invalidate(self, is_grid=False):
        if is_grid:
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
        else:
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True, grid_size=0)

    def explosion(self, head : Vector2):
        gmap.draw_block(self.explosion_radius, head, False)
        tank.check_hit(head, self.explosion_radius, self.damage)
        object.check_ground(head, self.explosion_radius)
        sprite.add_animation("Explosion", head, scale=self.explosion_radius/10)
        

    def get_head(self) -> Vector2:
        return self.center + (self.vector.normalized() * self.img_shell.w/gmap.CELL_SIZE)





fired_shells : list[Shell] = []

def add_shell(shell_name, head_position, theta):
    shell = Shell(shell_name, head_position, theta)
    shell_head = shell.get_head()
    position = head_position + (head_position - shell_head)*2
    gmap.draw_debug_point(position, 3)
    shell.set_pos(position)
    fired_shells.append(shell)
    object.add_object(shell)

    if shell_name == "MUL":
        for n in range(3):
            t = 0.05 * (n+1)
            shell_1 = Shell(shell_name, position, theta + t)
            shell_2 = Shell(shell_name, position, theta - t)
            fired_shells.append(shell_1)
            fired_shells.append(shell_2)
            object.add_object(shell_1)
            object.add_object(shell_2)
            


def delete_shell(shell : Shell):
    fired_shells.remove(shell)
    object.delete_object(shell)

def get_attributes(shell_name : str) -> tuple[float, float]:
    assert shell_name in SHELLS.keys()

    speed = 0
    damage = 0
    explosion_radius = 0

    if shell_name == "HP":
        speed = 15
        damage = 10
        explosion_radius = 15
    elif shell_name == "AP":
        speed = 18
        damage = 30
        explosion_radius = 8
    elif shell_name == "MUL":
        speed = 10
        damage = 2
        explosion_radius = 4
    else:
        raise Exception

    return speed, damage, explosion_radius