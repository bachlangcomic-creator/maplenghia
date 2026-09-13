import os
import sys
from pathlib import Path

APP_PAYLOAD = Path(os.environ["APP_PAYLOAD"])
sys.path.insert(0, str(APP_PAYLOAD))

from spotify_main_farm_orchestrator import SpotifyMainFarmOrchestrator, CONTINUE


class RecordingHost:
    def __init__(self):
        self.calls = []

    def _stage(self, name, owner):
        self.calls.append((name, owner))
        return CONTINUE

    def _spotify_mainfarm_state_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("STATE", owner)

    def _spotify_mainfarm_sell_safe_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("SELL_SAFE", owner)

    def _spotify_mainfarm_pet_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("PET", owner)

    def _spotify_mainfarm_recovery_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("RECOVERY", owner)

    def _spotify_mainfarm_buff1_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("BUFF1", owner)

    def _spotify_mainfarm_buff2_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("BUFF2", owner)

    def _spotify_mainfarm_dispatch_stage(self, cfg, pos, now, owner="SUPERVISOR"):
        return self._stage("DISPATCH", owner)


def test_c2_owner_runs_exact_recovered_stage_order():
    host = RecordingHost()
    SpotifyMainFarmOrchestrator(host).tick({}, (100.0, 170.0), 1.0, owner="C2")
    assert host.calls == [
        ("STATE", "C2"),
        ("SELL_SAFE", "C2"),
        ("PET", "C2"),
        ("RECOVERY", "C2"),
        ("BUFF1", "C2"),
        ("BUFF2", "C2"),
        ("DISPATCH", "C2"),
    ]


def test_source_has_single_c2_farm_owner_and_supervisor_skip():
    source = (APP_PAYLOAD / "maple_nghia_pro.py").read_text(encoding="utf-8")
    ws = source.index("    def _c2_fast_farm_worker")
    we = source.index("    @staticmethod\n    def _spotify_profile_kind_from", ws)
    worker = source[ws:we]
    assert 'spotify_main_farm_orchestrator.tick(' in worker
    assert 'owner="C2"' in worker
    assert "self.behavior_engine.tick(cfg, map_pos" not in worker
    bot = source[source.index("    def bot_loop"):]
    assert "if not c2_fast_owned:" in bot
    assert 'owner="SUPERVISOR"' in bot
