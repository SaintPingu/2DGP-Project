from tools import *

class Wind:
    def __init__(self):
        self.direction : int = 0
        self.speed : float = 0

    def randomize(self):
        rand_direction = random.randint(-1, 1)
        rand_speed = random.random() * 0.01
        self.direction = rand_direction
        self.speed = rand_speed
        print(self.direction)
        print(self.speed)
    
    def get_wind(self) -> Vector2:
        return Vector2(self.direction * self.speed, 0)
