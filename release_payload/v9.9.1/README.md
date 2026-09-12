# V9.9.1 All Cure Recovery

This overlay completes the Spotify All Cure workflow evidence and removes the permanent evidence block while preserving the safety gate.

Runtime readiness now requires:
1. `spotify_all_cure_market_enabled=true`;
2. recovered workflow evidence is complete;
3. all 12 external PNG templates validate under `user_data/all_cure_images`.

The Offline Spotify package references these PNGs as external files; they are not embedded in the supplied package. V9.9.1 therefore adds an all-or-nothing importer instead of bundling invented templates.
