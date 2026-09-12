from pathlib import Path
from spotify_all_cure_executor import SpotifyAllCureExecutor

class Gateway:
    def __init__(self,root): self.root=Path(root)
    def path_for(self,name):
        if '/' in name or name.startswith('.') or not name.endswith('.png'): raise ValueError(name)
        return self.root/name

class Host:
    def __init__(self): self.events=[]; self.cancelled=False
    def _spotify_market_cancelled(self,cfg): return self.cancelled
    def _spotify_market_find_asset(self,path,threshold): self.events.append(('find',Path(path).name,threshold)); return True
    def _spotify_market_wait_click(self,path,threshold,cfg): self.events.append(('wait_click',Path(path).name,threshold)); return True
    def _spotify_market_click_xy(self,x,y,cfg): self.events.append(('click_xy',x,y)); return True
    def _spotify_market_paste_text(self,text,cfg): self.events.append(('paste_text',text)); return True
    def _spotify_market_press_key(self,key,cfg): self.events.append(('press_key',key)); return True
    def _spotify_market_sleep(self,seconds,cfg): self.events.append(('sleep',seconds)); return True

def action_seq():
    return [
      {'op':'find','asset':'a.png','threshold':0.9,'evidence':'high_structural'},
      {'op':'wait_click','asset':'b.png','threshold':0.8,'evidence':'direct'},
      {'op':'click_xy','x':10,'y':20,'evidence':'high_structural'},
      {'op':'paste_text','text':'100','evidence':'direct'},
      {'op':'press_key','key':'ENTER','evidence':'high_structural'},
      {'op':'sleep','seconds':0.1,'evidence':'nghia_fallback'}]

def seed(root):
    root.mkdir(parents=True,exist_ok=True)
    for n in ('a.png','b.png'): (root/n).write_bytes(b'x')

def test_complete_sequence_executes_in_exact_order(tmp_path):
    seed(tmp_path); h=Host(); ex=SpotifyAllCureExecutor(h,Gateway(tmp_path)); assert ex.run(action_seq(),{})
    assert h.events==[('find','a.png',0.9),('wait_click','b.png',0.8),('click_xy',10.0,20.0),('paste_text','100'),('press_key','ENTER'),('sleep',0.1)]

def test_entire_schema_is_validated_before_first_side_effect(tmp_path):
    seed(tmp_path); h=Host(); ex=SpotifyAllCureExecutor(h,Gateway(tmp_path)); bad=action_seq(); bad[-1]={'op':'sleep','seconds':None,'evidence':'high_structural'}
    assert not ex.run(bad,{}) and h.events==[]

def test_unknown_op_bad_evidence_and_missing_asset_fail_closed(tmp_path):
    seed(tmp_path)
    for bad in ([{'op':'mystery','evidence':'direct'}],[{'op':'sleep','seconds':0.1,'evidence':'invented'}],[{'op':'find','asset':'missing.png','threshold':0.9,'evidence':'direct'}],[{'op':'find','asset':'../a.png','threshold':0.9,'evidence':'direct'}]):
        h=Host(); ex=SpotifyAllCureExecutor(h,Gateway(tmp_path)); assert not ex.run(bad,{}) and h.events==[]

def test_bridge_failure_stops_later_actions(tmp_path):
    seed(tmp_path); h=Host()
    def fail(path,threshold,cfg): h.events.append(('wait_click',Path(path).name,threshold)); return False
    h._spotify_market_wait_click=fail; ex=SpotifyAllCureExecutor(h,Gateway(tmp_path)); assert not ex.run(action_seq(),{})
    assert h.events==[('find','a.png',0.9),('wait_click','b.png',0.8)]

def test_cancellation_stops_without_followup_side_effects(tmp_path):
    seed(tmp_path); h=Host(); h.cancelled=True; ex=SpotifyAllCureExecutor(h,Gateway(tmp_path)); assert not ex.run(action_seq(),{}) and h.events==[]
