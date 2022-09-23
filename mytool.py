import pico2d
import scene

class Rect:
    def __init__(self, center=[0,0], width=0, height=0):
        self.center = [0,0]
        self.origin = [0,0]
        self.width = width
        self.height = height

        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

        self.set_pos(center)
    
    def set_origin(self, origin, width, height):
        self.width = width
        self.height = height
        self.origin = origin
        self.center = [origin[0] + (self.width//2), origin[1] + (self.height//2)]
        self.set_pos(self.center)

    def set_pos(self, center):
        self.center = center
        self.left = center[0] - (self.width//2)
        self.right = center[0] + (self.width//2)
        self.top = center[1] + (self.height//2)
        self.bottom = center[1] - (self.height//2)
        self.origin = (self.left, self.bottom)
    
    def update(self):
        self.set_pos(self.center)
        
    def collide_point(self, x, y):
        if x >= self.left and x <= self.right and y >= self.bottom and y <= self.top:
            return True
        return False

def convert_pico2d(x, y):
    return x, scene.screenHeight - 1 - y
    
def load_image_path(image : str):
    name = 'images/' + image
    result = pico2d.load_image(name)
    print('load : ' + name)
    return result

def out_of_range(x, y, max_x, max_y):
    return ((x < 0) or (x >= max_x) or (y < 0) or (y >= max_y))

