EXPECTED = {
    "LIE_B64": "83ffffe12bcf11e08018d5c96741d766e6f0fc2ce3998bf1e524835f7c5879ca",
    "DEAD_B64": "8ea188c8de3c991052f97a1f22837817f2b26fb93bd21faf6b3ea5755bf2adf8",
    "ONL_B64": "5f364d6314d83931bb5723f7b851d4245931b98b7926892862b5e0d052108303",
    "INV_FULL_B64": "548ae448c14c91788eaf3174b6fc9772dc1ea4b9bdeb09fff5b436c955e40c88",
    "INV_FULL_2_B64": "fe012da92940ce0a7ddaa92f074d8516be1a395603fd6747da66664b9d45e3f9",
    "INV_FULL_KOREA_B64": "6c9a383574b0c9bc69cb70841b7289d6c09056e331ec5c509507c1343dd4f720",
    "QUESTION_CAPTCHA_1_B64": "c0ff1925426b72a28c8ed1a429ec94abca495aa7ac139f753c01bea4e0947e53",
    "QUESTION_CAPTCHA_2_B64": "6113d88123bbfb56411239f4997b561371da19503170b3d71cc84514b5c044bf",
}


def test_exact_asset_hashes_are_locked():
    import hashlib
    import spotify_exact_assets as a

    assert a.EXACT_ASSET_SHA256 == EXPECTED
    for name, want in EXPECTED.items():
        raw = a.decode_exact_asset(name)
        assert hashlib.sha256(raw).hexdigest() == want
        assert a.verify_exact_asset(name)
