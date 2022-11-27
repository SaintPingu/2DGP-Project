if __name__ == "__main__":
    quit()

from tools import *
import object

class Ship(object.FlyObject):
    image : Image
    def __init__(self):
        self.dir = random.randint(0, 1) * 2 - 1 # Left or Right

        image_flip = ''
        xPos = -Ship.image.w * 2
        if self.dir == LEFT:
            image_flip = 'h'
            xPos = SCREEN_WIDTH + Ship.image.w * 2
        
        yPos = SCREEN_HEIGHT - self.image.h - random.randint(MAX_HEIGHT, SCREEN_HEIGHT - Ship.image.h)
        xPos, yPos = convert_pico2d(xPos, yPos)
        
        super().__init__(Ship.image, (xPos, yPos), Ship.image.w, Ship.image.h, dir=self.dir, image_flip=image_flip)

        self.speed = 300

    def update(self):
        self.move()

        is_destroy = False
        if self.dir == LEFT:
            if self.center.x <= -self.image.w:
                is_destroy = True
        elif self.dir == RIGHT:
            if self.center.x >= SCREEN_WIDTH + self.image.w:
                is_destroy = True

        if is_destroy:
            delete_ship()
            return False
        
        self.invalidate()
        return True


class AirDrop(object.GroundObject):
    image : Image
    def __init__(self, center):
        super().__init__(AirDrop.image, center, AirDrop.image.w, AirDrop.image.h)
        self.is_falling = True
    
    def update(self):
        if self.is_falling:
            self.fall()
            return False
        
        return True

    def fall(self):
        from gmap import check_collision_vectors
        vec_bot = self.get_vectors_bot()
        if check_collision_vectors(vec_bot) == True:
            self.is_falling = False
            self.rotate_ground()
            return

_air_drops : list[AirDrop]
_ship : Ship
_is_supply : bool
_is_reseted : bool

def enter():
    Ship.image = load_image_path('drop_ship.png')
    AirDrop.image = load_image_path('air_drop.png')

    global _ship
    _ship = None
    
    global _air_drops, _is_supply, _is_reseted
    _air_drops = []
    _is_supply = False
    _is_reseted = False

def exit():
    del Ship.image
    del AirDrop.image

    global _air_drops
    _air_drops.clear()
    del _air_drops

def update():
    global _is_reseted
    
    if _is_supply == False:
        return False
    
    if _ship == None:
        _is_reseted = False
        return False

    return True

def draw():
    pass

def reset():
    global _is_supply, _is_reseted

    if _is_reseted:
        return
    _is_reseted = True

    #_is_supply = random.randint(0, 1)
    _is_supply = True
    if _is_supply:
        create_ship()

def create_ship():
    global _ship
    if _ship != None:
        return

    _ship = Ship()
    object.add_object(_ship)

def delete_ship():
    global _ship, _is_reseted
    if _ship == None:
        return

    object.delete_object(_ship)
    _ship = None