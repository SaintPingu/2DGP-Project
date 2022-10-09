from tools import *
from object import *
import map
import scene


img_shell_ap : Image = None
img_shell_hp : Image = None
img_shell_mul : Image = None

SHELLS = {}

def init():
    global img_shell_hp, SHELLS
    img_shell_hp = load_image_path('shell_hp.png')
    SHELLS = {"AP" : img_shell_ap, "HP" : img_shell_hp, "MUL" : img_shell_mul}


class Shell(GameObject):
    def __init__(self, shell_name : str, position, theta):
        assert shell_name in SHELLS.keys()

        self.img_shell : Image = SHELLS[shell_name]
        super().__init__(position, self.img_shell.w, self.img_shell.h, theta)

        self.vector = Vector2.right().get_rotated(theta)
        self.speed, self.damage, self.explosion_radius = get_attributes(shell_name)
        self.temp = None

    def draw(self):
        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
        if self.temp:
            map.draw_debug_point(self.temp)
    
    def update(self):
        map.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
        self.offset(*(self.vector * self.speed))
        rect = self.get_squre()
        if rect.right < 0 or rect.left > scene.screenWidth or rect.bottom <= scene.min_height:
            fired_shells.remove(self)
            gameObjects.remove(self)
            return

        for object in gameObjects:
            if object is self:
                continue

            distance = (self.center - object.center).get_norm()
            if distance < self.detect_radius + object.detect_radius:
                object.invalidate()

        head = self.center + (self.vector.normalized() * self.img_shell.w/CELL_SIZE)
        rect_detection = Rect(head, CELL_SIZE, CELL_SIZE)
        detected_cells = map.get_detected_cells(rect_detection)
        if len(detected_cells) > 0:
            min = 99999
            for cell in detected_cells:
                cell_pos = Vector2(*map.get_pos_from_cell(*cell))
                distance = (cell_pos - head).get_norm()
                if distance <= CELL_SIZE + 1:
                    self.explosion(head)
                    fired_shells.remove(self)
                    gameObjects.remove(self)
                    return
                elif distance < min:
                    min = distance
                    self.temp = cell_pos
            print(min)

        self.is_rect_invalid = True
        self.vector = self.vector.lerp(Vector2.down(), 0.003)
        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y < 0:
            self.speed += 0.05
            self.theta *= -1

    def explosion(self, head : Vector2):
        map.set_block(self.explosion_radius, head, BLOCK_NONE)





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
        explosion_radius = 10
    else:
        raise Exception

    return speed, damage, explosion_radius