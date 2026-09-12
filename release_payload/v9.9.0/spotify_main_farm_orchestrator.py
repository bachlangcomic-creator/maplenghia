CONTINUE = "CONTINUE"
STOP_TICK = "STOP_TICK"


class SpotifyMainFarmOrchestrator:
    def __init__(self, host):
        self.host = host

    def tick(self, cfg, map_pos, now):
        stages = (
            self.host._spotify_mainfarm_state_stage,
            self.host._spotify_mainfarm_sell_safe_stage,
            self.host._spotify_mainfarm_pet_stage,
            self.host._spotify_mainfarm_recovery_stage,
            self.host._spotify_mainfarm_buff1_stage,
            self.host._spotify_mainfarm_buff2_stage,
            self.host._spotify_mainfarm_dispatch_stage,
        )
        for stage in stages:
            if stage(cfg, map_pos, now) == STOP_TICK:
                return STOP_TICK
        return CONTINUE
