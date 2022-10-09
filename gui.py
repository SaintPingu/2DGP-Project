from tools import *

class GUI:
    def __init__(self, image : Image, position):
        self.image = image
        self.position = position

    def draw(self):
        self.image.draw(*self.position)