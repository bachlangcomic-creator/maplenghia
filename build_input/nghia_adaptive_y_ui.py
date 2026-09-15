from __future__ import annotations

from typing import NamedTuple


class AdaptiveYUIState(NamedTuple):
    config_key: str | None
    enabled: bool
    checked: bool
    label: str


def adaptive_y_ui_state(map_name: str, *, c2_enabled: bool, b3_enabled: bool) -> AdaptiveYUIState:
    name = str(map_name or "").strip().upper()
    if name == "C2":
        checked = bool(c2_enabled)
        return AdaptiveYUIState(
            config_key="c2_adaptive_y_enabled",
            enabled=True,
            checked=checked,
            label=f"Adaptive Y • C2 • {'ON' if checked else 'OFF'}",
        )
    if name == "B3":
        checked = bool(b3_enabled)
        return AdaptiveYUIState(
            config_key="b3_adaptive_y_enabled",
            enabled=True,
            checked=checked,
            label=f"Adaptive Y • B3 • {'ON' if checked else 'OFF'}",
        )
    return AdaptiveYUIState(
        config_key=None,
        enabled=False,
        checked=False,
        label="Adaptive Y • không áp dụng cho map này",
    )
