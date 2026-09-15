import ctypes
import sys
import threading
import types
from pathlib import Path

class _DummyFunc:
    argtypes = None
    restype = None
    def __call__(self, *args, **kwargs):
        return 0

class _DummyLib:
    def __getattr__(self, name):
        return _DummyFunc()

if not hasattr(ctypes, 'windll'):
    ctypes.windll = types.SimpleNamespace(user32=_DummyLib(), kernel32=_DummyLib())

APP = (Path.cwd() / 'portable' / 'app_payload').resolve()
sys.path.insert(0, str(APP))

from maple_nghia_pro import MapleNghiaPro
from spotify_c2_runtime_support import C2PauseReasons, C2RuntimeTraceBuffer

class _Noop:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

class _Var:
    def __init__(self):
        self.value = None
    def set(self, value):
        self.value = value

class _BlockingBehaviorEngine:
    def __init__(self):
        self.input_lock = threading.RLock()
        self.running = True
        self.generation = 1
        self.semantic_state = 'FARM'
    def request_stop(self):
        self.running = False
        self.generation += 1
        self.semantic_state = 'IDLE'
    def release_inputs(self):
        with self.input_lock:
            return None
    def stop(self):
        self.request_stop()
        self.release_inputs()

def _make_client(engine):
    client = MapleNghiaPro.__new__(MapleNghiaPro)
    client.running = True
    client.behavior_engine = engine
    client.c2_pause_reasons = C2PauseReasons()
    client.c2_runtime_trace = C2RuntimeTraceBuffer(enabled=False)
    client.spotify_worker_supervisor = _Noop()
    client.spotify_main_farm_worker_generation = 10
    client.spotify_sell_inflight = True
    client.spotify_all_cure_market = _Noop()
    client.spotify_watchdog = _Noop()
    client.spotify_revive_state = _Noop()
    client.strategy_v10 = _Noop()
    client.spotify_primary_worker_generation = 20
    client.spotify_primary_watchdog_active = True
    client.target_tracker = _Noop()
    client.status_text = _Var()
    client.dashboard_status = _Var()
    client.side_status = _Noop()
    client.current_move_key = None
    client.spotify_primary_held_key = None
    client._input_keys_down = set()
    client._stop_requested = threading.Event()
    client._stop_cleanup_thread = None
    client._log = lambda *args, **kwargs: None
    client._c2_trace_dump = lambda *args, **kwargs: None
    client.release_move = lambda: None
    return client

def test_stop_button_does_not_wait_for_input_lock():
    engine = _BlockingBehaviorEngine()
    client = _make_client(engine)
    lock_held = threading.Event()
    release_holder = threading.Event()

    def holder():
        with engine.input_lock:
            lock_held.set()
            release_holder.wait(timeout=2.0)

    holder_thread = threading.Thread(target=holder, daemon=True)
    holder_thread.start()
    assert lock_held.wait(timeout=0.5)

    stop_done = threading.Event()
    def invoke_stop():
        client.stop_bot()
        stop_done.set()

    stop_thread = threading.Thread(target=invoke_stop, daemon=True)
    stop_thread.start()
    completed_while_lock_held = stop_done.wait(timeout=0.15)

    release_holder.set()
    holder_thread.join(timeout=1.0)
    stop_thread.join(timeout=1.0)

    assert completed_while_lock_held, 'STOP callback blocked waiting for input_lock'
    assert client.running is False
    assert client.spotify_main_farm_worker_generation > 10
    assert client.spotify_primary_worker_generation > 20
