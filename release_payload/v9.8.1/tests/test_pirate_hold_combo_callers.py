import inspect
from types import SimpleNamespace

import pytest
from spotify_recovered_core import SpotifyRecoveredCore


class Host(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.events=[]
        self.current_move_key=None
        self.map_move_direction=1
        self.spotify_pirate_farm_next_attack=0.0
        self.spotify_pirate_state='FARM'
        self.spotify_pirate_top_substate='MOVE_TOP'
        self.spotify_pirate_loot_substate='TO_START'
        self.spotify_pirate_loot_dir=1
        self.spotify_pirate_phase_started=0.0
        self.spotify_pirate_next_loot=999.0
        self.spotify_pirate_next_toploot=999.0
        self.spotify_pirate_last_loot=0.0
        self.spotify_pirate_last_toploot=0.0
        self.spotify_pirate_sweep_combo_done=False
        self.spotify_r54_pirate_sweep_burst_done=True
        self.spotify_pirate_next_loot_tap=999.0
        self.spotify_pirate_onehit_state='MOVE'
        self.spotify_pirate_onehit_wait_until=0.0
        self.spotify_pirate_onehit_attacked=False
    def __getattr__(self,name):
        if name.startswith('spotify_') or name.startswith('last_'):
            return 0
        raise AttributeError(name)
    def _log(self,text): self.events.append(('log',text))
    def _focus_game(self,cfg): return True
    def set_move(self,key): self.current_move_key=key; self.events.append(('move',key)); return True
    def release_move(self): self.current_move_key=None
    def _press_input_key(self,key,hold_ms=None): self.events.append(('press',key,hold_ms)); return True
    def _input_key_down(self,key): return True
    def _input_key_up(self,key): return True
    def _release_all_owned_inputs(self): self.current_move_key=None


def cfg():
    return {
        'left_key':'LEFT','right_key':'RIGHT','jump_key':'J','tele_key':'T','tele_enabled':True,
        'spotify_attack_key':'A','loot_key':'L','spotify_loot_enabled':True,'pause_on_focus_loss':False,
        'map_profile':{
            'LEFT_X':50,'LEFT_Y':172,'RIGHT_X':180,'RIGHT_Y':172,
            'LOOT_BOT_RIGHT_X':189,'LOOT_BOT_RIGHT_Y':196,
            'LOOT_BOT_LEFT_X':80,'LOOT_BOT_LEFT_Y':196,
            'LOOT_BOT_1_X':105,'LOOT_BOT_1_Y':201,
            'LOOT_BOT_2_X':170,'LOOT_BOT_2_Y':201,
        }
    }


def test_pirate_normal_farm_uses_flash_skill_shared_combo(monkeypatch):
    host=Host(); core=SpotifyRecoveredCore(host); calls=[]
    monkeypatch.setattr('spotify_recovered_core.random.randint', lambda a,b: 200)
    monkeypatch.setattr('spotify_recovered_core.time.monotonic', lambda: 10.1)
    monkeypatch.setattr(SpotifyRecoveredCore,'_spotify_hold_combo_action',lambda self,c,d,f,s,h: calls.append((d,f,s,h)) or True)
    assert core._spotify_pirate_normal_farm_step(cfg(),(100,172),10.0)
    assert calls == [('RIGHT','T','A',0.2)]


@pytest.mark.parametrize('one_hit,expected_hold',[(False,1.6),(True,1.5)])
def test_pirate_sweep_uses_shared_combo_with_exact_window(one_hit, expected_hold, monkeypatch):
    host=Host(); core=SpotifyRecoveredCore(host); calls=[]
    host.spotify_pirate_state='LOOTING_SWEEP'
    monkeypatch.setattr(SpotifyRecoveredCore,'_spotify_hold_combo_action',lambda self,c,d,f,s,h: calls.append((d,f,s,h)) or True)
    monkeypatch.setattr(SpotifyRecoveredCore,'_spotify_move_to_step',lambda *a,**k: False)
    monkeypatch.setattr('spotify_recovered_core.time.monotonic', lambda: 10.1)
    assert core._spotify_pirate_schedule_step(cfg(),(120,201),10.0,one_hit=one_hit)
    expected_dir = 'LEFT' if one_hit else 'RIGHT'
    assert calls == [(expected_dir,'T','A',expected_hold)]


def test_pirate_one_hit_farm_remains_one_hit_without_shared_combo():
    src=inspect.getsource(SpotifyRecoveredCore._spotify_pirate_1hit_farm_step)
    assert '_spotify_hold_combo_action' not in src
