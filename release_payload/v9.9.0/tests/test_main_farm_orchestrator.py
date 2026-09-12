from spotify_main_farm_orchestrator import SpotifyMainFarmOrchestrator, CONTINUE, STOP_TICK


class Host:
    def __init__(self, stop=None):
        self.events = []
        self.stop = stop

    def _stage(self, name):
        self.events.append(name)
        return STOP_TICK if self.stop == name else CONTINUE

    def _spotify_mainfarm_state_stage(self, c, p, n):
        return self._stage("state_gate")

    def _spotify_mainfarm_sell_safe_stage(self, c, p, n):
        return self._stage("sell_safe")

    def _spotify_mainfarm_pet_stage(self, c, p, n):
        return self._stage("pet")

    def _spotify_mainfarm_recovery_stage(self, c, p, n):
        return self._stage("lost_player_recovery")

    def _spotify_mainfarm_buff1_stage(self, c, p, n):
        return self._stage("buff1")

    def _spotify_mainfarm_buff2_stage(self, c, p, n):
        return self._stage("buff2")

    def _spotify_mainfarm_dispatch_stage(self, c, p, n):
        return self._stage("farm_dispatch")


def test_tick_runs_recovered_stage_order():
    h = Host()
    o = SpotifyMainFarmOrchestrator(h)
    assert o.tick({}, (100, 170), 1.0) == CONTINUE
    assert h.events == [
        "state_gate",
        "sell_safe",
        "pet",
        "lost_player_recovery",
        "buff1",
        "buff2",
        "farm_dispatch",
    ]


def test_sell_safe_short_circuits_later_stages():
    h = Host("sell_safe")
    o = SpotifyMainFarmOrchestrator(h)
    assert o.tick({}, None, 1.0) == STOP_TICK
    assert h.events == ["state_gate", "sell_safe"]


def test_state_gate_short_circuits_all_work():
    h = Host("state_gate")
    o = SpotifyMainFarmOrchestrator(h)
    assert o.tick({}, None, 1.0) == STOP_TICK
    assert h.events == ["state_gate"]


def test_recovery_short_circuits_buffs_and_dispatch():
    h = Host("lost_player_recovery")
    o = SpotifyMainFarmOrchestrator(h)
    assert o.tick({}, None, 1.0) == STOP_TICK
    assert h.events == ["state_gate", "sell_safe", "pet", "lost_player_recovery"]
