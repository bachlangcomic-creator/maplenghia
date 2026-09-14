V10.0.1 Spotify Stability — Y Preserved

Target branch: build-v10.0.1-spotify-stability
Upload this bundle preserving paths.

Scope:
- Keep C2/B3 Nghia Y logic exactly as V10.0.0.
- C2 remains Adaptive Y ON by default.
- B3 keeps its existing Adaptive Y toggle and V10.0.0 default (OFF unless user/config enables it).
- Stability correction only prevents Spotify 3.0s reacquire and Nghia fallback recovery from firing in the same exact-parity tick.
- Strategy V10 and maps.json remain hash-identical.

No latest.json or public release mutation is included.
