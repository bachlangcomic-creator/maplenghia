# Nghia Client v10.0.18 — MiuMiu Strict Sell

Base: **Nghia Client v10.0.17 — Custom SAFE ENTRY + Return To Farm**.

Changes:
- Only the MiuMiu card uses a verified **double left-click**. BAG, Cash, Sell Equip, ETC tab and Confirm remain single left-click.
- The mouse moves once, then performs two clicks under the same input lock; each click keeps the recovered 10–30 ms hold and uses an 80–120 ms inter-click gap.
- MiuMiu shop opening must be confirmed by `MIUMIU_OPENED_B64`; one bounded retry is allowed, with no click spam.
- Equip selling must see Confirm, click it successfully, and verify the Confirm dialog disappears.
- ETC selling uses the same strict Confirm verification and its result propagates to the full sell transaction.
- Removed false-success behavior including ignored Confirm results and `return sold_any or True`.
- Pirate ETC now fails safe when there is not enough evidence to prove an empty tab.

Preserved:
- V10.0.17 Custom SAFE ENTRY + post-sale Return To Farm.
- `maps.json`, `nghia_strategy_v10.py`, `spotify_recovered_core.py`, and `spotify_main_farm_orchestrator.py` remain byte-identical to v10.0.17.
- Farm map, movement, loot, TP, skill and unrelated features are unchanged.

Validation before stable promotion:
- 9 MiuMiu strict-sell tests.
- compileall.
- protected-core hash guards.
- fresh Windows/Nuitka build and PE check.
- launcher smoke and packaged smoke.
- updater package contract.
- published updater hash verification.
- `latest.json` is promoted only after all previous steps succeed.
