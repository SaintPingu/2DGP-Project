from tools import *

class GameObject:
    def __init__(self, center=(0,0), width=0, height=0, theta=0):
        self.center : Vector2 = Vector2(*center)
        self.width : float = width
        self.height : float = height

        self.theta : float = theta
        self.is_rect_invalid : bool = True
        self.is_created : bool = False

        self.dir : int = 0
        self.speed : float = 1

        detect_square = self.get_squre()
        self.detect_radius = (Vector2(*detect_square.center) - Vector2(detect_square.left, detect_square.top)).get_norm()
    
    def release(self):
        pass

    # update based on center, width, height, theta
    def update_object(self):
        self.is_rect_invalid = True

    def rotate(self, theta):
        self.theta += theta
        self.update_object()

    def set_theta(self, theta):
        if self.theta == theta:
            return
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
        self.center.x = center[0]
        self.center.y = center[1]
        self.update_object()

    def draw_image(self, image : Image, scale = 1):
        if self.is_rect_invalid == False:
            return
        self.is_rect_invalid = False
        image.rotate_draw(self.theta, *self.center, image.w*scale, image.h*scale)

    def get_rect(self):
        return Rect(tuple(self.center), self.width, self.height)
    
    def get_squre(self):
        width = self.width
        height = self.height
        if width < height:
            width = height
        else:
            height = width
        return Rect(self.center, width, height)
    
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
    
    def is_in_radius(self, position : Vector2, radius):
        distance = (position - self.center).get_norm()
        if distance < self.detect_radius + radius:
            return True

    def resize(self, scale : float):
        self.width *= scale
        self.height *= scale
        rect = self.get_rect()
        self.center.x = rect.origin[0] + self.width//2
        self.center.y = rect.origin[1] + self.height//2
        self.update_object()

    def draw(self):
        pass
    
    def update(self):
        pass
    
    def invalidate(self):
        pass



import gmap
class GroundObject(GameObject):
    def __init__(self, center=(0, 0), width=0, height=0, theta=0):
        super().__init__(center, width, height, theta)
        self.bot_left = Vector2()
        self.bot_right = Vector2()
        self.top_left = Vector2()
        self.top_right = Vector2()
        self.bot_center = Vector2()

        self.update_object()

    def update_object(self):
        self.bot_left.x = self.top_left.x = self.center.x - self.width//2
        self.bot_left.y = self.bot_right.y = self.center.y - self.height//2
        self.bot_right.x = self.top_right.x = self.center.x + self.width//2
        self.top_left.y = self.top_right.y = self.center.y + self.height//2
        
        self.bot_left = self.bot_left.get_rotated_origin(self.center, self.theta)
        self.bot_right = self.bot_right.get_rotated_origin(self.center, self.theta)
        self.top_left = self.top_left.get_rotated_origin(self.center, self.theta)
        self.top_right = self.top_right.get_rotated_origin(self.center, self.theta)

        vec_left_to_center = (self.bot_right - self.bot_left).normalized() * (self.width // 2)
        self.bot_center = self.bot_left + vec_left_to_center
        super().update_object()
    
    def get_vec_left(self):
        return (self.bot_left - self.bot_right).normalized()
    def get_vec_right(self):
        return (self.bot_right - self.bot_left).normalized()

    def get_vectors_bot(self):
        t = 0
        inc_t = 1 / (self.width * gmap.CELL_SIZE)

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

    def update_ground(self):
        if self.is_floating():
            self.attach_ground(True)

    # _BUG_ : pass through a thin wall
    def get_vec_highest(self, ignore_height=False):
        vectors_bot = self.get_vectors_bot()
        bot_cells = gmap.get_cells(vectors_bot)

        vec_highest = Vector2.zero()
        vec_befroe : Vector2 = None

        # Set max length
        max_length = 0
        idx_highest = 0
        if ignore_height or not self.is_created:
            max_length = float('inf')
        else:
            max_length = self.get_rect().height / 2

        # Find
        for idx, cell in enumerate(bot_cells):
            result = gmap.get_highest_ground_cell(cell[0], cell[1], max_length, True)
            if result is False:
                continue
            
            col, row = result
            _, height = gmap.get_pos_from_cell(col, row)
            if height > vec_highest.y:
                vec_highest.x = vectors_bot[idx].x
                vec_highest.y = height
                vec_befroe = vectors_bot[idx]
                idx_highest = idx

        return vec_befroe, vec_highest, idx_highest

    def attach_ground(self, ignore_height=False):
        vec_befroe, vec_pivot, idx_pivot = self.get_vec_highest(ignore_height)
        if vec_befroe is None:
            return False, False

        dy = vec_pivot.y - vec_befroe.y
        self.offset(0, dy)

        return vec_pivot, idx_pivot

    def rotate_ground(self, ignore_height=False):
        vec_pivot, idx_pivot = self.attach_ground(ignore_height)
        if vec_pivot is False:
            if self.is_created: # delete : fall
                self.invalidate()
                delete_object(self)
            return False
        vectors_bot = self.get_vectors_bot()

        # set rotation direction
        dir_check = LEFT
        if vec_pivot.x < self.bot_center.x:
            dir_check = RIGHT
            
        axis = Vector2()
        if dir_check == LEFT:
            axis = Vector2.left()
        else:
            axis = Vector2.right()

        max_y = self.bot_center.y + self.width//2
        min_y = self.bot_center.y - self.width//2
        # get minimum theta
        min_theta = float("inf")
        flat_count = 0
        for vector in vectors_bot:
            if dir_check == RIGHT:
                if vector.x < self.bot_center.x:
                    continue
            else:
                if vector.x > self.bot_center.x:
                    continue

            cell = gmap.get_cell(vector)
            if gmap.out_of_range_cell(cell[0], cell[1]):
                continue

            ground_cell = gmap.get_highest_ground_cell(*cell, is_cell=True)
            if ground_cell is False:
                continue
                
            vec_ground = Vector2(*gmap.get_pos_from_cell(*ground_cell))
            if vec_ground.y == vec_pivot.y:
                flat_count += 1
                continue
            elif vec_ground.y > max_y or vec_ground.y < min_y:
                continue
            
            theta = vec_ground.get_theta_axis(axis, vec_pivot)
            if dir_check == RIGHT:
                theta *= -1

            if math.fabs(theta) < math.fabs(min_theta):
                min_theta = theta
        
        # didn't find highest ground point for bottom vectors
        if min_theta == float("inf"):
            if flat_count > 0:
                min_theta = 0
            else:
                min_theta = self.theta
        elif math.fabs(math.degrees(min_theta)) > 75 and ignore_height == False:
            return False

        # rotation and set position to ground
        self.set_theta(min_theta)
        self.attach_ground()
        vectors_bot = self.get_vectors_bot()
        vector_correction = (vec_pivot - vectors_bot[idx_pivot])
        if vector_correction.x != 0 and vector_correction.y != 0:
            pass
        prev_center = self.center
        self.set_center((self.center[0] + vector_correction[0], self.center[1] + vector_correction[1]))
        if self.is_on_edge():
            self.set_center(prev_center)

        if self.is_floating():
            self.attach_ground()

        if self.is_on_edge():
            return False

        return True

    def is_on_edge(self):
        if self.dir == 0:
            return False

        vectors_bot = self.get_vectors_bot()
        max_length = self.width / 2
        for vector in vectors_bot:
            if self.dir == RIGHT:
                if vector.x < self.bot_center.x:
                    continue
            else:
                if vector.x > self.bot_center.x:
                    continue
            
            cell = gmap.get_cell(vector)
            ground_cell = gmap.get_highest_ground_cell(*cell, is_cell=True)
            if ground_cell is not False:
                ground_point = Vector2(*gmap.get_pos_from_cell(*ground_cell))
                length = (self.bot_center - ground_point).get_norm()
                if length <= max_length:
                    return False
        return True

    def is_floating(self):
        vectors_bot = self.get_vectors_bot()
        for vector in vectors_bot:
            cell = gmap.get_cell(vector)
            if gmap.get_block_cell(cell):
                return False
            
        return True

_gameObjects : list[GameObject]
_groundObjects : list[GroundObject]

def enter():
    global _gameObjects, _groundObjects
    _gameObjects = []
    _groundObjects = []
    
def exit():
    global _gameObjects, _groundObjects
    for object in _gameObjects:
        delete_object(object)
    _gameObjects.clear()
    _groundObjects.clear()
    del _gameObjects
    del _groundObjects

def add_object(object : GameObject):
    _gameObjects.append(object)
    if object.__class__.__base__ == GroundObject:
        _groundObjects.append(object)

def delete_object(object : GameObject):
    _gameObjects.remove(object)
    if object.__class__.__base__ == GroundObject:
        _groundObjects.remove(object)
    object.release()
    del object

def get_gameObjects():
    return _gameObjects

def update_objects():
    for object in _gameObjects:
        object.update()
                
def draw_objects():
    for object in reversed(_gameObjects):
        object.draw()

def check_ground(position : Vector2, radius):
    for object in _groundObjects:
        if object.is_in_radius(position, radius):
            object.rotate_ground(True)
            object.is_rect_invalid = True
            object.invalidate()