# Nghia Client v10.0.10 — Custom Map Parity

Base: **v10.0.9 MiuMiu Timer + CAPTCHA Client Capture**.

Changes:
- Custom `V10 PIRATE ROUTE` maps can optionally enable **SIMPLE Human Behavior**: a recovered-style 2% rest decision (3–5 seconds) and roughly 6% random jump decision (150–300 ms). Rest is implemented as non-blocking state so STOP remains responsive.
- Custom maps can optionally enable **B1/B3 Fall Recovery**: lane departure must remain outside the configured band for 2.5 seconds before vertical recovery is attempted.
- Custom maps can optionally enable **Loot Jitter kiểu Spotify**: the configured loot interval is multiplied by `random.uniform(0.9, 1.1)`.
- Custom maps can optionally enable **Adaptive Y cho Custom Map** independently of the existing Strategy V10 teleport-mode selector.
- All four new Custom Map options default **OFF**, preserving V10.0.9 custom-map behavior unless explicitly enabled.
- B3 Top Loot remains separate and is not merged into Custom Map parity.

Preserved from v10.0.9:
- Visible MiuMiu sell timer and live timer/minute runtime sync.
- CAPTCHA watchdog capture from Maple's exact 1280x720 client area.
- C2/B3 map-aware Adaptive Y.
- Anti-Jitter / Hysteresis and OFF bypass.
- STOP Non-Blocking.
- Existing Loot/TP/Skill/combat behavior outside the opted-in Custom Map extensions.
- Bundled `maps.json` is unchanged.

Stable publication requires V10.0.10 feature tests, V10.0.9 regressions, V10.0.8 Adaptive Y regressions, STOP regression, all 17 Anti-Jitter regressions, compileall, fresh Windows/Nuitka build, PE verification, launcher smoke, packaged smoke, published updater hash verification, and only then promotion of stable `latest.json` to `10.0.10`.
