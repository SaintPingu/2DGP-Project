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
        self.speed, self.damage = get_attributes(shell_name)

    def draw(self):
        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
    
    def update(self):
        map.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
        self.offset(*(self.vector * self.speed))
        rect = self.get_squre()
        if rect.right < 0 or rect.left > scene.screenWidth or rect.bottom <= scene.min_height:
            fired_shells.remove(self)
            gameObjects.remove(self)
            return

        self.is_rect_invalid = True
        self.vector = self.vector.lerp(Vector2.down(), 0.003)
        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y < 0:
            self.speed += 0.05
            self.theta *= -1

fired_shells : list[Shell] = []

def add_shell(shell : Shell):
    fired_shells.append(shell)
    gameObjects.append(shell)

    #fired_shells.clear()


def get_attributes(shell_name : str) -> tuple[float, float]:
    assert shell_name in SHELLS.keys()

    speed = 0
    damage = 0

    if shell_name == "HP":
        speed = 6
        damage = 10
    else:
        raise Exception

    return speed, damage