# Nghia V10.0.0 Strategy Engine Implementation Plan

Goal: implement the approved isolated V10 Strategy Engine without changing legacy map behavior.

Spec: `docs/superpowers/specs/2026-09-14-v10-strategy-engine-design.md`

Implementation sequence: pin the verified V9.9.8 candidate and hash protected legacy modules; add a new isolated `nghia_strategy_v10.py` resolver/validator/runtime with V10-owned state; integrate only through an explicit `ENGINE_MODE=STRATEGY_V10` gate in `maple_nghia_pro.py`; add V10-only Map Builder selectors and profile fields; then run regression tests, compileall, Nuitka, launcher smoke, packaged smoke, and artifact hash verification. The protected Spotify legacy modules must remain byte-for-byte unchanged. Public `latest.json` is out of scope.
