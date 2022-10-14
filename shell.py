from tools import *
from object import *
import gmap


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
        self.center_inv_list : list[Vector2] = []
        self.is_destroyed = False

    def draw(self):
        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
        if self.temp:
            gmap.draw_debug_point(self.temp)
    
    def update(self):
        from scene import SCREEN_WIDTH, min_height

        if len(self.center_inv_list) > 10 or self.is_destroyed:
            gmap.set_invalidate_rect(self.center_inv_list.pop(0), self.img_shell.w, self.img_shell.h, square=True)
            if len(self.center_inv_list) <= 0:
                fired_shells.remove(self)
                gameObjects.remove(self)
                return
            elif self.is_destroyed:
                return

        self.center_inv_list.append(Vector2(*self.center))
        # map.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
        self.offset(*(self.vector * self.speed))
        rect = self.get_squre()

        # out of range
        if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.top <= min_height:
            self.is_destroyed = True
            return

        # check collision
        for object in gameObjects:
            if object is self:
                continue

            distance = (self.center - object.center).get_norm()
            if distance < self.detect_radius + object.detect_radius:
                object.invalidate()

        # MODIFY
        # head size up
        head = self.get_head()
        detected_cell = gmap.get_cell(head)
        if not gmap.out_of_range_cell(detected_cell) and gmap.is_block_cell(detected_cell):
            self.explosion(head)
            self.is_destroyed = True
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
            return

        self.is_rect_invalid = True

        # apply rotation and gravity
        self.vector = self.vector.lerp(Vector2.down(), 0.003)
        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y < 0:
            self.speed += 0.05
            self.theta *= -1

    def explosion(self, head : Vector2):
        import sprite
        gmap.set_block(self.explosion_radius, head, BLOCK_NONE)

        head = self.get_head()
        sprite.add_animation("Explosion", head, scale=self.explosion_radius/10)

    def get_head(self) -> Vector2:
        return self.center + (self.vector.normalized() * self.img_shell.w/CELL_SIZE)





fired_shells : list[Shell] = []

def add_shell(shell : Shell):
    fired_shells.append(shell)
    gameObjects.append(shell)


def get_attributes(shell_name : str) -> tuple[float, float]:
    assert shell_name in SHELLS.keys()

    speed = 0
    damage = 0
    explosion_radius = 0

    if shell_name == "HP":
        speed = 6
        damage = 10
        explosion_radius = 20
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