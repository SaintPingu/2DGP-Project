if __name__ == "__main__":
    quit()

from tools import *

_crnt_bgm : Music = None
_sounds : list[Wav] = []

def play_bgm(name):
    global _crnt_bgm

    if _crnt_bgm != None:
        stop_bgm()
    
    name = 'bgm_' + name
    _crnt_bgm = load_music_path(name)
    _crnt_bgm.repeat_play()

def play_battle_bgm(index):
    name = 'battle_' + str(index)
    play_bgm(name)

def stop_bgm():
    global _crnt_bgm

    _crnt_bgm.stop()
    del _crnt_bgm
    _crnt_bgm = None


def add_sound(name, wav):
    name = 'sound_' + name