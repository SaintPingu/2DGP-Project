from object import GameObject
from tools import *
import gmap

SPRITES = {}

def init():
    global SPRITES
    img_sprite_shot = load_image_path('sprite_shot.png')
    img_sprite_explosion_hp = load_image_path('sprite_explosion.png')
    SPRITES = { "Shot" : img_sprite_shot, "Explosion" : img_sprite_explosion_hp }

class Sprite:
    def __init__(self, sprite_name:str, position, max_frame:int, frame_width:int, frame_height:int, theta=0, max_frame_col:int =0, delay:int=0, scale=1, is_play_once=True, origin=None):
        assert sprite_name in SPRITES.keys()

        self.sprite : Image = SPRITES[sprite_name]
        self.max_frame = max_frame
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frame = 0
        self.position = position
        self.is_play_once = is_play_once
        self.theta = theta
        self.delay = delay
        self.scale = scale
        self.max_frame_col = max_frame_col
        self.frame_row = 0
        self.crnt_delay = 0
        self.parent_object : GameObject = None

        self.raidus = 0
        if self.frame_width > self.frame_height:
            self.raidus = self.frame_width*self.scale
        else:
            self.raidus = self.frame_height*self.scale

        if origin is None:
            origin = (0, self.sprite.h)
        self.origin = Vector2(*origin)
        self.origin.y = self.sprite.h - self.origin.y
    
    def set_parent(self, object : GameObject):
        self.parent_object = object

    def draw(self):
        from tank import check_invalidate
        left = 0
        bottom = 0
        if self.frame_row != 0:
            left = self.origin.x + ((self.frame - (self.max_frame_col * self.frame_row)) * self.frame_width) 
            bottom = self.origin.y - (self.frame_row * self.frame_height)
        else:
            left = self.origin.x + (self.frame * self.frame_width) 
            bottom = self.origin.y

        if self.parent_object:
            self.parent_object.is_rect_invalid = True

        if self.theta != 0:
            self.sprite.clip_composite_draw(left, bottom, self.frame_width, self.frame_height, self.theta, '', *self.position, self.frame_width//2 * self.scale, self.frame_height//2 * self.scale)
        else:
            self.sprite.clip_draw(left, bottom, self.frame_width, self.frame_height, *self.position, self.frame_width*self.scale, self.frame_height*self.scale)

        
        check_invalidate(self.position, self.raidus)

    def update(self):
        is_running = True

        self.crnt_delay += 1
        if self.crnt_delay >= self.delay:
            self.crnt_delay = 0
            self.frame += 1
            if self.frame >= self.max_frame:
                if self.is_play_once:
                    is_running = False
            elif self.max_frame_col != 0:
                if self.frame % self.max_frame_col == 0:
                    self.frame_row += 1
            gmap.set_invalidate_rect(self.position, self.frame_width*self.scale, self.frame_height*self.scale, square=True)
        return is_running
    
animations : list[Sprite] = []

def add_animation(sprite_name : Sprite, center, theta=0, scale=1.0, parent=None):

    sprite = None
    if sprite_name == "Shot":
        sprite = Sprite("Shot", center, 4, 30, 48, theta, scale=scale, delay=5)
    elif sprite_name == "Explosion":
        sprite = Sprite(sprite_name, center, 14, 75, 75, max_frame_col=4, delay=5, scale=scale, origin=(0, 75))

    animations.append(sprite)

def update_animations():
    for animation in animations:
        if animation.update() is False:
            animations.remove(animation)

def draw_animations():
    for animation in animations:
        animation.draw()