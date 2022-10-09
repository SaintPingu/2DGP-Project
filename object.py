from tools import *

class GameObject:
    def __init__(self, center=(0,0), width=0, height=0, theta=0):
        self.center : Vector2 = Vector2(*center)
        self.width : float = width
        self.height : float = height

        self.bot_left = Vector2()
        self.bot_right = Vector2()
        self.top_left = Vector2()
        self.top_right = Vector2()
        self.bot_center = Vector2()

        self.theta : float = theta
        self.is_rect_invalid : bool = True
        self.is_created : bool = False

        self.dir : int = 0
        self.speed : float = 1

        self.update_object()

        detect_square = self.get_squre()
        self.detect_radius = (Vector2(*detect_square.center) - Vector2(detect_square.left, detect_square.top)).get_norm()

    def update_object(self):
        self.bot_left.x = self.top_left.x = self.center.x - self.width//2
        self.bot_left.y = self.bot_right.y = self.center.y - self.height//2
        self.bot_right.x = self.top_right.x =  self.center.x + self.width//2
        self.top_left.y = self.top_right.y = self.center.y + self.height//2
        
        self.bot_left = self.bot_left.get_rotated_origin(self.center, self.theta)
        self.bot_right = self.bot_right.get_rotated_origin(self.center, self.theta)
        self.top_left = self.top_left.get_rotated_origin(self.center, self.theta)
        self.top_right = self.top_right.get_rotated_origin(self.center, self.theta)

        vec_left_to_center = (self.bot_right - self.bot_left).normalized() * (self.width // 2)
        self.bot_center = self.bot_left + vec_left_to_center
        self.is_rect_invalid = True

    def rotate(self, theta):
        self.theta += theta
        self.update_object()

    def set_theta(self, theta):
        self.theta = theta
        self.update_object()

    def rotate_pivot(self, theta, pivot):
        center = self.center
        self.center = center.get_rotated_origin(pivot, theta)
        self.theta = theta
        self.update_object()

    def offset(self, dx, dy):
        self.center.x += dx
        self.center.y += dy
        self.update_object()

    def set_center(self, center):
        self.center = Vector2(*center)
        self.update_object()

    def draw_image(self, image : Image):
        if self.is_rect_invalid == False:
            return
        self.is_rect_invalid = False
        image.rotate_draw(self.theta, *self.center)

    def get_rect(self):
        return Rect(self.center, self.width, self.height)
    
    def get_squre(self):
        width = self.width
        height = self.height
        if width < height:
            width = height
        else:
            height = width
        return Rect(self.center, width, height)

    def get_vec_left(self):
        return (self.bot_left - self.bot_right).normalized()
    def get_vec_right(self):
        return (self.bot_right - self.bot_left).normalized()
    
    def out_of_bound(self, left= -9999, top= -9999, right= -9999, bottom= -9999):
        rect = self.get_rect()

        if left != -9999 and rect.left < left:
            return True
        elif top != -9999 and rect.top > top:
            return True
        elif right != -9999 and rect.right > right:
            return True
        elif bottom != -9999 and rect.bottom < bottom:
            return True

        return False

    def set_pos(self, center):
        self.set_center(center)

    def draw_debug_rect(self):
        rect = self.get_rect()
        draw_rectangle(rect.left, rect.bottom, rect.right, rect.top)

    def draw(self):
        pass
    
    def update(self):
        pass
    
    def invalidate(self):
        pass




class GroundObject(GameObject):
    def get_vectors_bot(self):
        t = 0
        inc_t = 1 / self.width

        result : list[Vector2] = []
        while t <= 1:
            position = self.bot_left.lerp(self.bot_right, t)
            result.append(position)
            t += inc_t

        return result

    def move(self):
        if self.dir == 0:
            return
        elif self.dir == LEFT:
            self.vDir = self.get_vec_left()
        else:
            self.vDir = self.get_vec_right()

        vDest = self.center + (self.vDir * self.speed)

        if self.set_pos(vDest) == False:
            self.stop()

    def start_move(self, dir):
        self.dir += dir

    def stop(self):
        self.dir = 0

gameObjects : list[GameObject] = []

def update_objects():
    for object in gameObjects:
        object.update()
                
def draw_objects():
    for object in gameObjects:
        object.draw()