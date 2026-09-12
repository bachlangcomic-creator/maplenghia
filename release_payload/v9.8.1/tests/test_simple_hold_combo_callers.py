import inspect
from types import SimpleNamespace

import pytest
from spotify_recovered_core import SpotifyRecoveredCore


class Host(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.events=[]
        self.current_move_key='RIGHT'
        self.spotify_primary_held_key=None
        self.spotify_primary_skill_next=0.0
        self.spotify_primary_skill_phase=0
        self.spotify_primary_last_action=0.0
        self.spotify_scheduler_last_action=''
        self.spotify_human_pause_until=0.0
        self.last_jump_time=0.0
        self.map_move_direction=1
        self.spotify_pirate_farm_next_attack=0.0
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


def simple_cfg(name, tele=True):
    return {
        'current_map': name,
        'spotify_attack_key':'A', 'tele_key':'T', 'tele_enabled':tele,
        'jump_key':'J', 'pause_on_focus_loss':False,
    }


@pytest.mark.parametrize('map_name',['C1','C2','B1','B3'])
def test_simple_maps_use_shared_helper_with_flash_and_200_500ms(map_name, monkeypatch):
    host=Host(); core=SpotifyRecoveredCore(host); calls=[]
    monkeypatch.setattr('spotify_recovered_core.random.random', lambda: 0.9)
    monkeypatch.setattr('spotify_recovered_core.random.randint', lambda a,b: 200)
    monkeypatch.setattr('spotify_recovered_core.time.sleep', lambda _s: None)
    monkeypatch.setattr('spotify_recovered_core.time.monotonic', lambda: 10.1)
    def shared(self,cfg,direction,flash,skill,hold):
        calls.append((direction,flash,skill,hold)); return True
    monkeypatch.setattr(SpotifyRecoveredCore,'_spotify_hold_combo_action',shared)
    monkeypatch.setattr(SpotifyRecoveredCore,'_spotify_c2_tp_skill_hold_combo',lambda *a,**k: (_ for _ in ()).throw(AssertionError('legacy C2 caller active')))
    assert core._spotify_primary_skill_step(simple_cfg(map_name),10.0)
    assert calls == [('RIGHT','T','A',0.2)]


def test_simple_tele_disabled_passes_none(monkeypatch):
    host=Host(); core=SpotifyRecoveredCore(host); calls=[]
    monkeypatch.setattr('spotify_recovered_core.random.random', lambda: 0.9)
    monkeypatch.setattr('spotify_recovered_core.random.randint', lambda a,b: 500)
    monkeypatch.setattr('spotify_recovered_core.time.sleep', lambda _s: None)
    monkeypatch.setattr('spotify_recovered_core.time.monotonic', lambda: 10.1)
    monkeypatch.setattr(SpotifyRecoveredCore,'_spotify_hold_combo_action',lambda self,cfg,direction,flash,skill,hold: calls.append((direction,flash,skill,hold)) or True)
    assert core._spotify_primary_skill_step(simple_cfg('C2', tele=False),10.0)
    assert calls == [('RIGHT',None,'A',0.5)]


def test_non_target_hold_users_are_moved_to_legacy_helper():
    src = inspect.getsource(SpotifyRecoveredCore)
    assert 'def _spotify_hold_action_legacy' in src
    bunny = inspect.getsource(SpotifyRecoveredCore._spotify_bunny_step)
    top = inspect.getsource(SpotifyRecoveredCore._spotify_pirate_schedule_step)
    assert '_spotify_hold_action_legacy' in bunny
    assert '_spotify_hold_action_legacy' in top
