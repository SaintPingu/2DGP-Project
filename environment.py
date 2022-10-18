from tools import *
import object
import gui
import gmap

class Wind:
    def __init__(self):
        self.image_cloud = load_image_path('gui_cloud.png')
        self.image_wind = load_image_path('gui_wind_lines.png')
        pos_cloud = (SCREEN_WIDTH//2, SCREEN_HEIGHT - self.image_cloud.h)
        self.wind_pos_left = (pos_cloud[0] - self.image_cloud.w, pos_cloud[1])
        self.wind_pos_right = (pos_cloud[0] + self.image_cloud.w, pos_cloud[1])
        gui_cloud = gui.GUI(self.image_cloud, pos_cloud)
        self.gui_wind = gui.GUI(self.image_wind, is_draw=False)
        gui.add_gui(gui_cloud)
        gui.add_gui(self.gui_wind)
        
        self.direction : int = 0
        self.speed : float = 0
    
    def release(self):
        del self.image_cloud
        del self.image_wind

    def randomize(self):
        gmap.set_invalidate_rect(self.gui_wind.position, self.image_wind.w, self.image_wind.h)
        rand_direction = random.randint(-1, 1)
        rand_speed = 0.001 + random.random() * 0.01
        self.direction = rand_direction
        self.speed = rand_speed

        self.gui_wind.is_draw = False
        self.gui_wind.flip = ''
        if self.direction < 0:
            self.gui_wind.is_draw = True
            self.gui_wind.position = self.wind_pos_left
            self.gui_wind.flip = 'h'
        elif self.direction > 0:
            self.gui_wind.is_draw = True
            self.gui_wind.position = self.wind_pos_right
            
    
    def get_wind(self) -> Vector2:
        return Vector2(self.direction * self.speed, 0)


_CLOUD_MIN_HEIGHT = 800
_CLOUD_IMAGE_COUNT = 9
class Cloud(object.GameObject):
    def __init__(self):
        super().__init__()
        self.wind = gmap.wind
        self.image : Image = None
        self.scale = 0
        self.randomize(True)

    def draw(self):
        self.draw_image(self.image, self.scale)
    
    def resize(self):
        self.width = self.image.w * self.scale
        self.height = self.image.h * self.scale
        rect = self.get_rect()
        self.center = Vector2(rect.origin[0] + self.width//2, rect.origin[1] + self.height//2)
        self.update_object()

    def get_random_image(self):
        index = random.randrange(0, _CLOUD_IMAGE_COUNT)
        return _images_cloud[index]

    def randomize(self, is_init=False):
        self.image = self.get_random_image()
        self.scale = 1 + random.random()
        self.width = self.image.w * self.scale
        self.height = self.image.h * self.scale

        rand_x = random.randint(0, 500)
        y = random.randint(_CLOUD_MIN_HEIGHT, SCREEN_HEIGHT)
        if is_init:
            x = random.randint(0, SCREEN_WIDTH)
            self.set_center((x, y))
        elif self.wind.direction < 0:
            self.set_pos((SCREEN_WIDTH + self.width//2 + rand_x, y))
        elif self.wind.direction > 0:
            self.set_pos((-self.width//2 - rand_x, y))
            
        self.resize()

    def update(self):
        rect_inv = Rect(self.center, self.width + 3, self.height + 3)
        gmap.resize_rect_inv(rect_inv)
        gmap.draw_background(rect_inv)
        speed = self.wind.speed * 100
        self.offset(self.wind.direction * speed, 0)
        self.is_rect_invalid = True

        rect = self.get_rect()
        if rect.right < 0 and self.wind.direction < 0:
            self.randomize()
        elif rect.left > SCREEN_WIDTH and self.wind.direction > 0:
            self.randomize()
            

_images_cloud : list[Image]

def enter(cloud_count=10):
    global _images_cloud
    _images_cloud = []

    for i in range(_CLOUD_IMAGE_COUNT):
        image = load_image_path('cloud_' + str(i) + '.png')
        image.opacify(0.7)
        _images_cloud.append(image)
    
    for _ in range(cloud_count):
        object.add_object(Cloud())

def exit():
    global _images_cloud
    
    for image in _images_cloud:
        del image
    _images_cloud.clear()
    del _images_cloud