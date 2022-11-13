if __name__ == "__main__":
    quit()

from tools import *
import object
import gui
import gmap
import framework

_BASE_WIND_SPEED_MPS = 5
_BASE_WIND_SPEED_PPS = (_BASE_WIND_SPEED_MPS * PIXEL_PER_METER)
_WIND_AFFECT = 0.1

_clouds : list[object.GameObject] = None

def enter(cloud_count=10):
    global _images_cloud
    _images_cloud = []

    for i in range(_CLOUD_IMAGE_COUNT):
        image = load_image_path('cloud_' + str(i) + '.png')
        image.opacify(0.7)
        _images_cloud.append(image)

    global _clouds
    _clouds = []

    for _ in range(cloud_count):
        object.add_object(Cloud())

    global wind
    wind = Wind()
    wind.randomize()

def exit():
    global _images_cloud
    
    for image in _images_cloud:
        del image
    _images_cloud.clear()
    del _images_cloud

    global wind
    wind.release()
    del wind

    global _clouds
    _clouds.clear()
    _clouds = None

def toggle_show_clouds():
    for cloud in _clouds:
        cloud.toggle_show()

class Wind:
    def __init__(self):
        self.image_cloud = load_image_path('gui_cloud.png')
        self.image_wind = load_image_path('gui_wind_lines.png')
        pos_cloud = (SCREEN_WIDTH//2, SCREEN_HEIGHT - self.image_cloud.h)
        self.wind_pos_left = (pos_cloud[0] - self.image_cloud.w, pos_cloud[1])
        self.wind_pos_right = (pos_cloud[0] + self.image_cloud.w, pos_cloud[1])
        gui_cloud = gui.GUI(self.image_cloud, pos_cloud)
        self.gui_wind = gui.GUI(self.image_wind, is_draw=False)
        gui.add_gui(gui_cloud, 1)
        gui.add_gui(self.gui_wind, 1)
        
        self.direction : int = 0
        self.speed : float = 0
    
    def release(self):
        del self.image_cloud
        del self.image_wind

    def randomize(self):
        gmap.set_invalidate_rect(self.gui_wind.position, self.image_wind.w, self.image_wind.h)
        rand_direction = random.randint(-1, 1)
        rand_speed = _BASE_WIND_SPEED_PPS / (random.random() + 0.1)
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
            
    
    def get_wind_vector(self) -> Vector2:
        return Vector2(self.direction * self.speed * _WIND_AFFECT, 0)


_CLOUD_MIN_HEIGHT = 800
_CLOUD_IMAGE_COUNT = 9
class Cloud(object.GameObject):
    def __init__(self):
        super().__init__()
        self.image : Image = None
        self.scale = 0
        self.randomize(True)

        global _clouds
        _clouds.append(self)

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
        elif wind.direction < 0:
            self.set_pos((SCREEN_WIDTH + self.width//2 + rand_x, y))
        elif wind.direction > 0:
            self.set_pos((-self.width//2 - rand_x, y))
            
        self.resize()

    def update(self):
        rect_inv = Rect(self.center, self.width + 4, self.height + 4)
        gmap.draw_background(rect_inv, False)
        speed = wind.speed
        self.offset(wind.direction * speed * framework.frame_time, 0)
        self.is_rect_invalid = True

        rect = self.get_rect()
        if rect.right < 0 and wind.direction < 0:
            self.randomize()
        elif rect.left > SCREEN_WIDTH and wind.direction > 0:
            self.randomize()
            

_images_cloud : list[Image]
wind : Wind = None
