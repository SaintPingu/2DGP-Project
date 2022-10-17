class GameState:
    def __init__(self, state):
        self.enter = state.enter
        self.exit = state.exit
        self.pause = state.pause
        self.resume = state.resume
        self.handle_events = state.handle_events
        self.update = state.update
        self.draw = state.draw

running = None
stack = None

def change_state(state):
    global stack
    if (len(stack) > 0):
        stack[-1].exit()
        stack.pop()
    stack.append(state)
    state.enter()



def push_state(state):
    global stack
    if (len(stack) > 0):
        stack[-1].pause()
    stack.append(state)
    state.enter()



def pop_state():
    global stack
    if (len(stack) > 0):
        stack[-1].exit()
        stack.pop()

    if (len(stack) > 0):
        stack[-1].resume()



def quit():
    global running
    running = False


# current_time = time.time() + 1
def run(start_state):
    global running, stack
    running = True
    stack = [start_state]
    start_state.enter()

    while (running):
        # frame_time = time.time() - current_time
        # frame_rate = 1.0 / frame_time
        # current_time += frame_time
        # if frame_rate < 60:
        #     print("Frame Time: %f sec, Frame Rate: %f fps" %(frame_time,frame_rate))

        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()
    while (len(stack) > 0):
        stack[-1].exit()
        stack.pop()