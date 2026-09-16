"""Maple client-area capture geometry for the Spotify watchdog.

The exact CAPTCHA detector expects a 1280x720 game frame. This helper converts
Maple's cached HWND client origin into desktop coordinates so the watchdog
captures the game client instead of the user's full desktop region.
"""
from __future__ import annotations

import ctypes

SPOTIFY_GAME_WIDTH = 1280
SPOTIFY_GAME_HEIGHT = 720


class _RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def client_capture_region(user32, hwnd, expected_width=SPOTIFY_GAME_WIDTH,
                          expected_height=SPOTIFY_GAME_HEIGHT):
    """Return ``(left, top, width, height)`` for an exact Maple client area.

    Returns ``None`` if the HWND is invalid, Win32 queries fail, or the client
    size is not the recovered Spotify 1280x720 invariant.
    """
    if not hwnd:
        return None
    rect = _RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None
    width = int(rect.right - rect.left)
    height = int(rect.bottom - rect.top)
    if (width, height) != (int(expected_width), int(expected_height)):
        return None
    point = _POINT(0, 0)
    if not user32.ClientToScreen(hwnd, ctypes.byref(point)):
        return None
    return int(point.x), int(point.y), width, height
