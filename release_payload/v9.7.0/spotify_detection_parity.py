from dataclasses import dataclass

CAPTCHA_ROI = (300, 200, 650, 350)  # left, top, width, height
CAPTCHA_PRIMARY_THRESHOLD = 0.70
CAPTCHA_SECONDARY_THRESHOLD = 0.68
FULL_BAG_DETECT_THRESHOLD = 0.35
SELL_THRESHOLD = 0.65

SOURCE_EXACT = "spotify_exact"
SOURCE_STRUCTURAL = "spotify_structural"
SOURCE_NGHIA_FALLBACK = "nghia_fallback"
_ALLOWED = {SOURCE_EXACT, SOURCE_STRUCTURAL, SOURCE_NGHIA_FALLBACK}


@dataclass(frozen=True)
class SpotifyDetectionResult:
    kind: str
    matched: bool
    score: float | None
    threshold: float | None
    source: str


def crop_captcha_roi(frame, game_size):
    if tuple(game_size) != (1280, 720):
        raise ValueError("exact Spotify CAPTCHA ROI requires 1280x720")
    left, top, width, height = CAPTCHA_ROI
    return frame[top : top + height, left : left + width]


def score_result(kind, score, threshold, source, *, exact_asset=False):
    if source not in _ALLOWED:
        raise ValueError("unknown detector evidence source")
    if source == SOURCE_EXACT and not exact_asset:
        raise ValueError("spotify_exact requires recovered/validated exact asset path")
    score = float(score)
    threshold = float(threshold)
    return SpotifyDetectionResult(str(kind), score >= threshold, score, threshold, source)
