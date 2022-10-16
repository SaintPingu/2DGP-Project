from tools import *
from object import *
import gmap
import sprite


SHELLS = {}

def init():
    global SHELLS
    img_shell_ap = load_image_path('shell_ap.png')
    img_shell_hp = load_image_path('shell_hp.png')
    img_shell_mul = load_image_path('shell_multiple.png')
    SHELLS = { "AP" : img_shell_ap, "HP" : img_shell_hp, "MUL" : img_shell_mul }


class Shell(GameObject):
    def __init__(self, shell_name : str, position, theta):
        assert shell_name in SHELLS.keys()

        self.img_shell : Image = SHELLS[shell_name]
        super().__init__(position, self.img_shell.w, self.img_shell.h, theta)

        self.vector = Vector2.right().get_rotated(theta)
        self.speed, self.damage, self.explosion_radius = get_attributes(shell_name)
        self.temp = None
        self.is_destroyed = False
        self.wind : gmap.env.Wind = gmap.wind

    def draw(self):
        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
        if self.temp:
            gmap.draw_debug_point(self.temp)
    
    def update(self):
        gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)

        dest = (self.center + self.vector * self.speed) + self.wind.get_wind()
        self.vector = self.vector.get_rotated_dest(self.center, dest)
        self.set_center(dest)

        rect = self.get_squre()

        # out of range
        if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.top <= MIN_HEIGHT:
            delete_shell(self)
            return

        # check collision
        for object in get_gameObjects():
            if type(object) is Shell:
                continue

            distance = (self.center - object.center).get_norm()
            if distance < self.detect_radius + object.detect_radius:
                object.invalidate()

        head = self.get_head()
        rect_detection = Rect(head, 4, 4)
        detected_cells = get_detected_cells(rect_detection)
        for detected_cell in detected_cells:
            if not out_of_range_cell(*detected_cell) and get_block_cell(detected_cell):
                self.explosion(head)
                gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
                delete_shell(self)
                return
        if is_debug_mode():
            gmap.draw_debug_rect(rect_detection)

        self.is_rect_invalid = True

        # apply rotation and gravity
        self.vector = self.vector.lerp(Vector2.down(), 0.003)
        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y < 0:
            self.speed += 0.05
            self.theta *= -1

    def explosion(self, head : Vector2):
        gmap.draw_block(self.explosion_radius, head, False)
        check_ground(head, self.explosion_radius)
        sprite.add_animation("Explosion", head, scale=self.explosion_radius/10)
        

    def get_head(self) -> Vector2:
        return self.center + (self.vector.normalized() * self.img_shell.w/CELL_SIZE)





fired_shells : list[Shell] = []

def add_shell(shell : Shell):
    fired_shells.append(shell)
    add_object(shell)

def delete_shell(shell : Shell):
    fired_shells.remove(shell)
    delete_object(shell)

def get_attributes(shell_name : str) -> tuple[float, float]:
    assert shell_name in SHELLS.keys()

    speed = 0
    damage = 0
    explosion_radius = 0

    if shell_name == "HP":
        speed = 6
        damage = 10
        explosion_radius = 15
    elif shell_name == "AP":
        speed = 7
        damage = 30
        explosion_radius = 8
    elif shell_name == "MUL":
        speed = 5
        damage = 2
        explosion_radius = 4
    else:
        raise Exception

    return speed, damage, explosion_radius