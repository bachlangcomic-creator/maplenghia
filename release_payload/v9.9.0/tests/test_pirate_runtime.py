from types import SimpleNamespace
import spotify_recovered_core as mod

def host_for_pirate():
    return SimpleNamespace(spotify_pirate_onehit_state='RIGHT_SETUP',spotify_pirate_onehit_wait_until=0.0,spotify_pirate_onehit_attacked=False,map_move_direction=1,spotify_pirate_farm_next_attack=0.0,current_move_key=None)
def cfg():
    return {'map_profile':{'LEFT_X':100,'RIGHT_X':200,'LEFT_Y':180,'RIGHT_Y':180},'left_key':'LEFT','right_key':'RIGHT','jump_key':'SPACE','skill_key':'A','tele_key':'T','tele_enabled':True}
def test_onehit_right_setup_uses_recovered_seconds_window(monkeypatch):
    h=host_for_pirate();c=mod.SpotifyRecoveredCore(h);monkeypatch.setattr(mod.SpotifyRecoveredCore,'_spotify_pirate_fall_recovery',lambda *a,**k:False);monkeypatch.setattr(mod.SpotifyRecoveredCore,'_spotify_move_to_step',lambda *a,**k:True);h.release_move=lambda:None;monkeypatch.setattr(mod.random,'uniform',lambda a,b:0.3);monkeypatch.setattr(mod.time,'monotonic',lambda:100.0);assert c._spotify_pirate_1hit_farm_step(cfg(),(178,183),100.0);assert h.spotify_pirate_onehit_wait_until==100.3
def test_onehit_left_edge_uses_exact_1_5_second_wait(monkeypatch):
    h=host_for_pirate();h.spotify_pirate_onehit_state='MOVE';h.map_move_direction=-1;c=mod.SpotifyRecoveredCore(h);monkeypatch.setattr(mod.SpotifyRecoveredCore,'_spotify_pirate_fall_recovery',lambda *a,**k:False);h.release_move=lambda:None;h._log=lambda *a,**k:None;assert c._spotify_pirate_1hit_farm_step(cfg(),(104,180),50.0);assert h.spotify_pirate_onehit_wait_until==51.5
def test_normal_right_edge_uses_recovered_jump_and_settle(monkeypatch):
    h=host_for_pirate();events=[];c=mod.SpotifyRecoveredCore(h);h.release_move=lambda:events.append(('release',));monkeypatch.setattr(mod.SpotifyRecoveredCore,'_spotify_input_semantic',lambda self,cfg,role,key,**kw:events.append((role,key,kw.get('hold_ms'))) or True);monkeypatch.setattr(mod.random,'random',lambda:0.079);monkeypatch.setattr(mod.random,'randint',lambda a,b:150);monkeypatch.setattr(mod.time,'sleep',lambda s:events.append(('sleep',s)));assert c._spotify_pirate_normal_farm_step(cfg(),(196,180),10.0);assert ('JUMP','SPACE',150) in events;assert ('sleep',0.05) in events;assert h.map_move_direction==-1
