if __name__ == "__main__":
    quit()

from tools import *
import object
import gmap
import sprite
import tank
import sound
import framework

DEFAULT_SHELL = "AP"

SHELLS : dict
EXPLOSIONS : dict

def enter():
    global SHELLS, EXPLOSIONS, fired_shells
    img_shell_ap = load_image_path('shell_ap.png')
    img_shell_hp = load_image_path('shell_hp.png')
    img_shell_mul = load_image_path('shell_multiple.png')
    img_shell_nuclear = load_image_path('shell_nuclear.png')
    img_shell_teleport = load_image_path('shell_teleport.png')
    SHELLS = { "AP" : img_shell_ap, "HP" : img_shell_hp, "MUL" : img_shell_mul, "NUCLEAR" : img_shell_nuclear, "TP" : img_shell_teleport}
    EXPLOSIONS = {
        "AP" : "Explosion",
        "HP" : "Explosion",
        "MUL" : "Explosion",
        "NUCLEAR" : "Explosion_Nuclear",
    }

    fired_shells = []

def exit():
    global SHELLS, EXPLOSIONS, fired_shells
    for image in SHELLS.values():
        del image
    del SHELLS
    
    EXPLOSIONS.clear()
    del EXPLOSIONS
    
    for shell in fired_shells:
        delete_shell(shell)

    fired_shells.clear()
    del fired_shells


class Shell(object.GameObject):
    MIN_POWER = 0.1
    def __init__(self, shell_name : str, position, theta, power = 1, is_simulation=False, delay = 0):
        self.img_shell : Image = get_shell_image(shell_name)

        super().__init__(position, self.img_shell.w, self.img_shell.h, theta)

        self.shell_name = shell_name
        self.origin = position
        self.start_theta = theta

        self.vector = Vector2.right().get_rotated(theta)
        self.speed, self.shell_damage, self.explosion_damage, self.explosion_radius = get_attributes(shell_name)
        if self.speed <= 0:
            raise Exception

        if power < Shell.MIN_POWER:
            power = Shell.MIN_POWER
        self.speed *= power

        self.is_destroyed = False
        self.DETECTION_RADIUS = 2
        self.prev_head : Vector2() = None

        self.is_simulation = is_simulation
        if is_simulation:
            self.shell_damage = 0
            self.explosion_damage = 0

        self.t = 0
        self.delay = delay
        self.sub = False
        self.is_teleport = False

    def draw(self):
        if self.delay > 0:
            return

        self.is_rect_invalid = True
        self.draw_image(self.img_shell)
    
    def move(self):
        dest = Vector2()
        
        # Use projectile moition formula
        if not self.is_simulation:
            self.t += (self.speed/20 * framework.frame_time)
            dest.x = self.origin[0] + (self.speed * self.t * math.cos(self.start_theta))
            dest.y = self.origin[1] + (self.speed * self.t * math.sin(self.start_theta) - (0.5 * GRAVITY * self.t**2))
        else:
            self.t += 0.15 # faster search
            dest.x = self.origin[0] + (self.speed * self.t * math.cos(self.start_theta))
            dest.y = self.origin[1] + (self.speed * self.t * math.sin(self.start_theta) - (0.5 * GRAVITY * self.t**2))

        dest += gmap.env.wind.get_wind_vector() * self.t
        self.vector = self.vector.get_rotated_dest(self.center, dest)
        self.set_center(dest)
        

    def update(self):
        if self.delay > 0:
            self.delay -= framework.frame_time
            if self.delay <= 0 and not self.sub:
                sprite.add_animation("Shot", self.origin, self.start_theta)
                sound.play_sound('tank_fire', 64)
            return

        self.invalidate()
        rect = self.get_squre()

        # out of range
        if rect.right < 0 or rect.left > SCREEN_WIDTH or rect.top <= MIN_HEIGHT:
            delete_shell(self)
            return False
        
        head = self.get_head()
        if self.prev_head is None:
            self.prev_head = head

        collision_vectors = gmap.get_vectors(head, self.prev_head)

        target_tank = self.check_tanks(head, collision_vectors)
        if target_tank is not False:
            return target_tank
        elif self.check_grounds(head) == True:
            return False

        self.is_rect_invalid = True

        self.theta = self.vector.get_theta(Vector2.right())
        if self.vector.y <= 0:
            self.theta *= -1
            
        self.move()
        self.prev_head = head

        return True
    
    # Check collision by tanks
    def check_tanks(self, head, collision_vectors):
        head = self.get_head()
        target_tank = tank.check_hit(head, collision_vectors, self.DETECTION_RADIUS, self.shell_damage)
        if target_tank is False:
            return False

        explosion_pos = head + (target_tank.center - head)*0.5
        self.explosion(explosion_pos)
        return target_tank

    # Check collision by grounds
    def check_grounds(self, head):
        rect_detection = Rect(head, self.DETECTION_RADIUS*2, self.DETECTION_RADIUS*2)
        detected_cells = gmap.get_detected_cells(rect_detection)
        if is_debug_mode():
            gmap.draw_debug_rect(rect_detection)

        for detected_cell in detected_cells:
            if not gmap.out_of_range_cell(*detected_cell) and gmap.get_block_cell(detected_cell):
                self.explosion(head)
                return True
        return False

    def invalidate(self, is_grid=False):
        if self.is_simulation:
            return

        if is_grid:
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True)
        else:
            gmap.set_invalidate_rect(self.center, self.img_shell.w, self.img_shell.h, square=True, grid_size=0)

    def explosion(self, head : Vector2):
        if self.is_simulation:
            return

        if self.is_teleport:
            tank.teleport(head)
        else:
            gmap.draw_block(self.explosion_radius, head, False)
            tank.check_explosion(head, self.explosion_radius, self.explosion_damage)
            object.check_ground(head, self.explosion_radius)
            sprite.add_animation(EXPLOSIONS[self.shell_name], head, scale=self.explosion_radius/10)
            self.invalidate()
            sound.play_sound('explosion', 100)

        delete_shell(self)

    def get_head(self) -> Vector2:
        return self.center + (self.vector.normalized() * self.img_shell.w/gmap.CELL_SIZE)

    def set_sub(self):
        self.sub = True





fired_shells : list[Shell]

def add_shell(shell_name, head_position, theta, power = 1, item = None):
    delay = 0
    count_shot = 1
    if item == "double":
        count_shot = 2

    for i in range(count_shot):
            
        shell = Shell(shell_name, head_position, theta, power, delay=delay)
        shell_head = shell.get_head()
        position = head_position + (head_position - shell_head)
        shell.set_pos(position)
        fired_shells.append(shell)
        object.add_object(shell)

        if shell_name == "MUL" and item != "TP":
            for n in range(3):
                t = 0.05 * (n+1)
                shell_1 = Shell(shell_name, position, theta + t, power, delay=delay)
                shell_2 = Shell(shell_name, position, theta - t, power, delay=delay)
                shell_1.set_sub()
                shell_2.set_sub()
                fired_shells.append(shell_1)
                fired_shells.append(shell_2)
                object.add_object(shell_1)
                object.add_object(shell_2)

        delay += 2

    
    if item == "extension":
        for shell in fired_shells:
            shell.explosion_radius *= 2
    elif item == "TP":
        shell.is_teleport = True
        shell.shell_damage = 0
        shell.img_shell = get_shell_image("TP")
        shell.speed = get_attributes("TP")[0]
            


def delete_shell(shell : Shell):
    if shell.is_simulation is True:
        return

    if shell in fired_shells:    
        fired_shells.remove(shell)
        object.delete_object(shell)

def get_attributes(shell_name : str) -> tuple[float, float]:
    speed = 0
    shell_damage = 0
    explosion_damage = 0
    explosion_radius = 0

    if shell_name == "HP":
        speed = 100
        shell_damage = 20
        explosion_damage = 20 
        explosion_radius = 15
    elif shell_name == "AP":
        speed = 120
        shell_damage = 30
        explosion_damage = 5
        explosion_radius = 8
    elif shell_name == "MUL":
        speed = 80
        shell_damage = 5
        explosion_damage = 10
        explosion_radius = 4
    elif shell_name == "NUCLEAR":
        speed = 110
        shell_damage = 5
        explosion_damage = 30
        explosion_radius = 22
    elif shell_name == "TP":
        speed = 80
    else:
        raise Exception

    return speed, shell_damage, explosion_damage, explosion_radius

def get_shell_image(shell_name):
    assert shell_name in SHELLS.keys()

    return SHELLS[shell_name]