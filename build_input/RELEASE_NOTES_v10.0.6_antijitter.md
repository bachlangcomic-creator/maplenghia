# Nghia Client v10.0.6 — Anti-Jitter / Hysteresis Candidate

Base: **v10.0.6 STOP Non-Blocking**.

This candidate adds an optional Anti-Jitter / Hysteresis decision gate while keeping the original v10.0.6 path available with the toggle OFF.

Changes:
- Visible `Anti-Jitter / Hysteresis • OFF = V10.0.6 gốc` checkbox in the real CustomTkinter farm UI opened by `app_payload/run.bat`.
- OFF is a true bypass and clears Anti-Jitter state.
- ON uses 2 consecutive edge samples, a 0.40 s turn lock, and 8 px departure hysteresis.
- SIMPLE/C1/C2/B1/B3, Pirate2 farm movement, Pirate2 1-Hit MOVE, Bunny transitions, and Stand Still anchor drift are guarded.
- Anti-Jitter never presses/releases keys itself and fails open if its own logic errors.
- V10.0.6 STOP Non-Blocking behavior is preserved.

Validation required by the release workflow:
- exact final source SHA checks;
- 17/17 Anti-Jitter and STOP regression tests;
- Python compileall;
- fresh Windows/Nuitka build;
- launcher smoke on the rebuilt portable client;
- second launcher smoke after unpacking the packaged Windows candidate.

This candidate is published under a separate tag and does **not** change stable `latest.json`, because its internal semantic version is still `10.0.6`.
