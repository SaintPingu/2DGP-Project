from tools import *
import gui
import gmap

class Wind:
    def __init__(self):
        image_cloud = load_image_path('gui_cloud.png')
        self.image_wind = load_image_path('gui_wind_lines.png')
        pos_cloud = (SCREEN_WIDTH//2, SCREEN_HEIGHT - image_cloud.h)
        self.wind_pos_left = (pos_cloud[0] - image_cloud.w, pos_cloud[1])
        self.wind_pos_right = (pos_cloud[0] + image_cloud.w, pos_cloud[1])
        gui_cloud = gui.GUI(image_cloud, pos_cloud)
        self.gui_wind = gui.GUI(self.image_wind, is_draw=False)
        #gui.add_gui(gui_cloud)
        #gui.add_gui(self.gui_wind)
        
        self.direction : int = 0
        self.speed : float = 0

    def randomize(self):
        gmap.set_invalidate_rect(self.gui_wind.position, self.image_wind.w, self.image_wind.h)
        rand_direction = random.randint(-1, 1)
        rand_speed = random.random() * 0.01
        self.direction = rand_direction
        self.speed = rand_speed
        print(self.direction)

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
