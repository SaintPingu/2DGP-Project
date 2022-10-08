from mytool import *
import map
import tank

screenWidth = 1280
screenHeight = 800

img_map : Image
img_background : Image
img_ground : Image



def init():
    global img_background, img_map, img_ground
    open_canvas(screenWidth, screenHeight, sync=True)
    img_background = load_image_path('background.png')
    img_map = load_image_path('map_1.png')
    img_ground = load_image_path('ground.png')
    img_map.draw(screenWidth//2, screenHeight//2, screenWidth, screenHeight)

    map.init()
    map.read_mapfile(1)

def draw_scene():
    tank.update()
    map.draw_map()
    update_canvas()