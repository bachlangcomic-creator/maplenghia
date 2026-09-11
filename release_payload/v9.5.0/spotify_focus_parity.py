"""Spotify-style cached focus state for Nghia.

The original Spotify runtime has a dedicated ~0.2s focus worker.  This module
keeps all Win32 calls out of Nghia's C2 hot path: worker code refreshes the
cache, while combat reads the cached boolean/HWND only.
"""
from __future__ import annotations

import threading
from typing import Callable, Optional

FOCUS_PARITY_MIGRATION_KEY = "spotify_focus_parity_cache_v2"
SPOTIFY_WINDOW_TITLE_EXACT = "MapleStory Worlds-MAPLE PLANET"


def focus_parity_enabled_from_config(data: dict) -> bool:
    """One-time migration: existing v9.4.x configs default into parity A.

    Once the migration marker is persisted, the user's explicit checkbox choice
    is respected on later launches.
    """
    if not bool(data.get(FOCUS_PARITY_MIGRATION_KEY, False)):
        return True
    return bool(data.get("spotify_force_focus_parity", True))


class SpotifyFocusCache:
    """Thread-safe exact-title focus cache.

    ``find_exact`` is expected to wrap FindWindowW.  Combat-side callers use only
    ``cached_has_focus``/``cached_hwnd`` and therefore perform no Win32 lookup.
    """

    def __init__(
        self,
        find_exact: Callable[[str], Optional[int]],
        get_foreground: Callable[[], Optional[int]],
        force_foreground: Callable[[int], bool],
    ) -> None:
        self._find_exact = find_exact
        self._get_foreground = get_foreground
        self._force_foreground = force_foreground
        self._lock = threading.RLock()
        self.hwnd: Optional[int] = None
        self.title = ""
        self.focused = False

    @staticmethod
    def _candidate_titles(configured_title: str, fixed_title: str):
        seen = set()
        # Prefer the Spotify exact title when a generic substring such as
        # "MapleStory Worlds" is configured.  Keep configured exact titles as a
        # compatibility candidate for users whose client title differs.
        for title in (fixed_title, configured_title):
            title = str(title or "").strip()
            if title and title not in seen:
                seen.add(title)
                yield title

    def refresh(self, configured_title: str, fixed_title: str, force: bool = False) -> bool:
        hwnd = None
        title = ""
        for candidate in self._candidate_titles(configured_title, fixed_title):
            try:
                found = self._find_exact(candidate)
            except Exception:
                found = None
            if found:
                hwnd = int(found)
                title = candidate
                break

        if not hwnd:
            with self._lock:
                self.hwnd = None
                self.title = ""
                self.focused = False
            return False

        try:
            actual = self._get_foreground()
        except Exception:
            actual = None
        focused = bool(actual == hwnd)

        if force and not focused:
            try:
                self._force_foreground(hwnd)
            except Exception:
                pass
            try:
                actual = self._get_foreground()
            except Exception:
                actual = None
            focused = bool(actual == hwnd)

        with self._lock:
            self.hwnd = hwnd
            self.title = title
            self.focused = focused
        return focused

    def cached_has_focus(self) -> bool:
        with self._lock:
            return bool(self.hwnd and self.focused)

    def cached_hwnd(self) -> Optional[int]:
        with self._lock:
            return self.hwnd

    def clear(self) -> None:
        with self._lock:
            self.hwnd = None
            self.title = ""
            self.focused = False
