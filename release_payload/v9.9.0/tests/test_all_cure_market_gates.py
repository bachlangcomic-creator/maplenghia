import binascii,json,struct,zlib
from pathlib import Path
from spotify_all_cure_assets import REQUIRED_ALL_CURE_ASSETS
from spotify_all_cure_market import SpotifyAllCureMarketWorker

def chunk(kind,data):
    body=kind+data; return struct.pack('>I',len(data))+body+struct.pack('>I',binascii.crc32(body)&0xffffffff)
def tiny_png():
    sig=b'\x89PNG\r\n\x1a\n'; ihdr=struct.pack('>IIBBBBB',1,1,8,0,0,0,0); return sig+chunk(b'IHDR',ihdr)+chunk(b'IDAT',zlib.compress(b'\x00\x00'))+chunk(b'IEND',b'')
def seed_assets(root):
    root.mkdir(parents=True,exist_ok=True)
    for n in REQUIRED_ALL_CURE_ASSETS:(root/n).write_bytes(tiny_png())
def evidence(path,ready):
    path.write_text(json.dumps({'workflow_evidence_ready':ready,'buy_actions':[{'op':'find','asset':'empty.png','threshold':0.9,'evidence':'direct'}],'sell_actions':[{'op':'find','asset':'empty.png','threshold':0.9,'evidence':'direct'}],'loop_delays_seconds':{'buy_to_sell':{'value':1.0},'failure_retry':{'value':2.0}},'unresolved':[] if ready else ['x']}),encoding='utf-8')
class Host:
    def __init__(self):self.events=[];self.runtime_cfg={}
    def _log(self,msg):self.events.append(('log',msg))
    def _spotify_market_cancelled(self,cfg):return False
    def _spotify_market_run_action(self,name,actions,cfg):self.events.append(('run_action',name,len(actions)));return True
def make(tmp_path,ready=True,assets=True):
    ep=tmp_path/'evidence.json';evidence(ep,ready);ad=tmp_path/'assets'
    if assets:seed_assets(ad)
    return Host(),ep,ad
def side_effects(h):return [x for x in h.events if x[0]!='log']
def test_config_false_blocks_even_with_assets_and_workflow(tmp_path):
    h,ep,ad=make(tmp_path);w=SpotifyAllCureMarketWorker(h,ep,ad);assert not w.request_buy({'spotify_all_cure_market_enabled':False});assert side_effects(h)==[]
def test_missing_asset_blocks(tmp_path):
    h,ep,ad=make(tmp_path);(ad/'empty.png').unlink();w=SpotifyAllCureMarketWorker(h,ep,ad);assert not w.request_buy({'spotify_all_cure_market_enabled':True});assert side_effects(h)==[]
def test_incomplete_workflow_blocks(tmp_path):
    h,ep,ad=make(tmp_path,False,True);w=SpotifyAllCureMarketWorker(h,ep,ad);assert not w.request_buy({'spotify_all_cure_market_enabled':True});assert side_effects(h)==[]
def test_all_three_gates_allow_exactly_one_executor_transaction(tmp_path):
    h,ep,ad=make(tmp_path);w=SpotifyAllCureMarketWorker(h,ep,ad);assert w.request_buy({'spotify_all_cure_market_enabled':True});assert side_effects(h)==[('run_action','buy',1)]
