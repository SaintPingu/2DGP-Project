if __name__ == "__main__":
    quit()

from tools import *

_crnt_bgm : Music = None
_sounds : dict[str, Wav] = {}

def play_bgm(name):
    global _crnt_bgm

    if _crnt_bgm != None:
        stop_bgm()
    
    file_name = 'bgm_' + name
    _crnt_bgm = load_music_path(file_name)
    _crnt_bgm.repeat_play()

def play_battle_bgm(index):
    file_name = 'battle_' + str(index)
    play_bgm(file_name)

def stop_bgm():
    global _crnt_bgm

    _crnt_bgm.stop()
    del _crnt_bgm
    _crnt_bgm = None


def add_sound(name):
    global _sounds
    
    if name in _sounds.keys():
        return

    file_name = 'sound_' + name
    wav = load_wav_path(file_name)

    _sounds[name] = wav

def del_sounds():
    for sound in _sounds.values():
        del sound
    _sounds.clear()

def play_sound(name, volume=128, channel=-1):
    assert(name in _sounds)

    wav = _sounds[name]
    wav.set_volume(volume)
    Mix_PlayChannel(channel, wav.wav, 0)

def stop_sound(name):
    assert(name in _sounds)

    _sounds[name].set_volume(0)


def enter(state : str):
    if state == 'battle':
        add_sound('tank_fire')
        add_sound('explosion')
        add_sound('tank_explosion')
        add_sound('tank_movement')
    else:
        assert(0)