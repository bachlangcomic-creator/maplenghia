from pathlib import Path
import importlib.util
import json

APP = Path("portable/app_payload")


def load_helper():
    p = APP / "nghia_adaptive_y_ui.py"
    spec = importlib.util.spec_from_file_location("nghia_adaptive_y_ui", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_c2_maps_to_c2_variable_and_label():
    mod = load_helper()
    state = mod.adaptive_y_ui_state("C2", c2_enabled=True, b3_enabled=False)
    assert state.config_key == "c2_adaptive_y_enabled"
    assert state.enabled is True
    assert state.checked is True
    assert state.label == "Adaptive Y • C2 • ON"


def test_b3_maps_to_b3_variable_and_label():
    mod = load_helper()
    state = mod.adaptive_y_ui_state("b3", c2_enabled=True, b3_enabled=False)
    assert state.config_key == "b3_adaptive_y_enabled"
    assert state.enabled is True
    assert state.checked is False
    assert state.label == "Adaptive Y • B3 • OFF"


def test_other_maps_disable_control():
    mod = load_helper()
    state = mod.adaptive_y_ui_state("C1", c2_enabled=True, b3_enabled=True)
    assert state.config_key is None
    assert state.enabled is False
    assert state.checked is False
    assert state.label == "Adaptive Y • không áp dụng cho map này"


def test_compact_ui_wires_map_aware_toggle_to_runtime_config():
    text = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
    assert "self.adaptive_y_checkbox = ctk.CTkCheckBox(" in text
    assert "command=self._on_adaptive_y_map_toggle" in text
    assert "def _sync_adaptive_y_map_toggle(self):" in text
    assert "def _on_adaptive_y_map_toggle(self):" in text
    assert "self.runtime_cfg[state.config_key] = enabled" in text
    assert "_spotify_reset_c2_adaptive_y_state(clear_anchor=True)" in text
    assert "self._sync_adaptive_y_map_toggle()" in text


def test_v1008_version_metadata_present():
    version = json.loads(Path("portable/version.json").read_text(encoding="utf-8"))
    assert version["version"] == "10.0.8"
    text = (APP / "nghia_spotify_nologin.py").read_text(encoding="utf-8")
    assert "Nghia Edition V10.0.8" in text
