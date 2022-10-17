import os
from tools import *
import framework
import state_title

os.chdir(os.path.dirname(__file__))

open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT, sync=True)
framework.run(state_title)
close_canvas()