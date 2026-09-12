from dataclasses import dataclass

CAPTCHA_ROI = (300, 200, 650, 350)  # left, top, width, height
CAPTCHA_PRIMARY_THRESHOLD = 0.70
CAPTCHA_SECONDARY_THRESHOLD = 0.68
FULL_BAG_DETECT_THRESHOLD = 0.35
SELL_THRESHOLD = 0.65
DISCONNECT_THRESHOLD = 0.95

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


from spotify_exact_assets import decode_exact_asset, verify_exact_asset


def exact_asset_result(kind, score, threshold, asset_name, *, path_is_exact):
    if not verify_exact_asset(asset_name):
        raise ValueError("exact Spotify asset hash mismatch")
    source = SOURCE_EXACT if path_is_exact else SOURCE_STRUCTURAL
    return score_result(
        kind,
        score,
        threshold,
        source,
        exact_asset=(source == SOURCE_EXACT),
    )


def detect_captcha_exact(frame, game_size, matcher):
    roi = crop_captcha_roi(frame, game_size)
    score = float(matcher(roi, decode_exact_asset("LIE_B64")))
    return exact_asset_result(
        "captcha",
        score,
        CAPTCHA_PRIMARY_THRESHOLD,
        "LIE_B64",
        path_is_exact=True,
    )


def score_full_bag_variant(asset_name, score, *, path_is_exact):
    if asset_name not in {"INV_FULL_B64", "INV_FULL_2_B64", "INV_FULL_KOREA_B64"}:
        raise ValueError("unknown recovered inventory-full asset")
    return exact_asset_result(
        "full_bag",
        score,
        FULL_BAG_DETECT_THRESHOLD,
        asset_name,
        path_is_exact=path_is_exact,
    )


def score_dead(score, *, threshold, path_is_exact):
    return exact_asset_result(
        "dead",
        score,
        threshold,
        "DEAD_B64",
        path_is_exact=path_is_exact,
    )


def score_disconnect(score, *, threshold, path_is_exact):
    return exact_asset_result(
        "disconnect",
        score,
        threshold,
        "ONL_B64",
        path_is_exact=path_is_exact,
    )


def detect_disconnect_recovered(frame, matcher):
    if not verify_exact_asset("ONL_B64"):
        raise ValueError("exact Spotify asset hash mismatch")
    score = float(matcher(frame, decode_exact_asset("ONL_B64")))
    return score_result(
        "disconnect",
        score,
        DISCONNECT_THRESHOLD,
        SOURCE_STRUCTURAL,
        exact_asset=False,
    )
