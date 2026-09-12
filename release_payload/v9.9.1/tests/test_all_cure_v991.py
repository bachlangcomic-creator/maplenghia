import json
import os
import struct
import tempfile
import zlib
from pathlib import Path

import pytest

from spotify_all_cure_assets import REQUIRED_ALL_CURE_ASSETS, SpotifyAllCureAssetGateway
from spotify_all_cure_market import SpotifyAllCureMarketWorker

APP = Path(os.environ['APP_PAYLOAD'])
EVIDENCE = Path(os.environ['V991_EVIDENCE'])


def png_bytes(rgb=(12, 34, 56)):
    import binascii
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', binascii.crc32(kind + data) & 0xFFFFFFFF)
    raw = b'\x00' + bytes(rgb)
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def write_all_assets(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(REQUIRED_ALL_CURE_ASSETS):
        (folder / name).write_bytes(png_bytes((i % 255, (i + 1) % 255, (i + 2) % 255)))


def test_recovered_evidence_has_no_null_thresholds_and_is_ready():
    data = json.loads((EVIDENCE / 'all_cure_market.json').read_text(encoding='utf-8'))
    assert data['workflow_evidence_ready'] is True
    assert data.get('unresolved') == []
    for action in data['buy_actions'] + data['sell_actions']:
        if action['op'] in {'find', 'wait_click'}:
            assert isinstance(action['threshold'], (int, float))
            assert 0.0 <= action['threshold'] <= 1.0

    buy = {a.get('asset'): a['threshold'] for a in data['buy_actions'] if a['op'] in {'find', 'wait_click'}}
    assert buy == {
        'empty.png': 0.90,
        'npc_all_cure.png': 0.50,
        'all_cure_line.png': 0.50,
        'confirm_all_cure.png': 0.20,
        'buy_all_cure.png': 0.20,
        'finish_buying.png': 0.70,
    }
    sell = [(a.get('asset'), a['threshold']) for a in data['sell_actions'] if a['op'] == 'wait_click']
    assert sell == [
        ('shop.png', 0.20), ('exit.png', 0.20), ('all_cure_pots.png', 0.75),
        ('set_sell_item.png', 0.60), ('confirm_set_item_to_sell.png', 0.20),
        ('complete_set_item.png', 0.20), ('exit.png', 0.70),
    ]


def test_import_is_all_or_nothing_and_makes_gateway_ready():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src, dst = root / 'src', root / 'user_data' / 'all_cure_images'
        write_all_assets(src)
        dst.mkdir(parents=True)
        (dst / 'old.txt').write_text('old', encoding='utf-8')
        gateway = SpotifyAllCureAssetGateway(dst)
        result = gateway.import_from_directory(src)
        assert result.ready is True
        assert gateway.validate().ready is True
        assert not (dst / 'old.txt').exists()
        assert sorted(p.name for p in dst.iterdir()) == sorted(REQUIRED_ALL_CURE_ASSETS)


def test_missing_or_invalid_source_never_mutates_existing_destination():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src, dst = root / 'src', root / 'dest'
        write_all_assets(src)
        (src / REQUIRED_ALL_CURE_ASSETS[-1]).unlink()
        dst.mkdir(parents=True)
        sentinel = dst / 'keep.txt'
        sentinel.write_text('keep', encoding='utf-8')
        gateway = SpotifyAllCureAssetGateway(dst)
        result = gateway.import_from_directory(src)
        assert result.ready is False
        assert result.missing == (REQUIRED_ALL_CURE_ASSETS[-1],)
        assert sentinel.read_text(encoding='utf-8') == 'keep'
        assert list(dst.iterdir()) == [sentinel]

        write_all_assets(src)
        (src / REQUIRED_ALL_CURE_ASSETS[0]).write_bytes(b'not a png')
        result = gateway.import_from_directory(src)
        assert result.ready is False
        assert REQUIRED_ALL_CURE_ASSETS[0] in result.invalid
        assert sentinel.read_text(encoding='utf-8') == 'keep'
        assert list(dst.iterdir()) == [sentinel]


def test_worker_readiness_transitions_to_ready_when_templates_present():
    class Host:
        def _log(self, msg):
            pass
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        evidence = root / 'evidence.json'
        evidence.write_text(json.dumps({
            'workflow_evidence_ready': True,
            'unresolved': [],
            'buy_actions': [{'op':'find','asset':'empty.png','threshold':0.9,'evidence':'direct'}],
            'sell_actions': [{'op':'wait_click','asset':'shop.png','threshold':0.2,'evidence':'high_structural'}],
        }), encoding='utf-8')
        asset_dir = root / 'all_cure_images'
        worker = SpotifyAllCureMarketWorker(Host(), evidence_path=evidence, asset_dir=asset_dir)
        state, detail = worker.readiness_status()
        assert state == 'MISSING'
        assert '12' in detail
        write_all_assets(asset_dir)
        state, detail = worker.readiness_status()
        assert state == 'READY'
        assert '12/12' in detail


def test_host_exposes_all_cure_import_and_status_ui_contract():
    source = (APP / 'maple_nghia_pro.py').read_text(encoding='utf-8')
    assert 'self.spotify_all_cure_status = tk.StringVar' in source
    assert 'def _refresh_all_cure_status(' in source
    assert 'def _import_all_cure_templates(' in source
    assert 'NẠP 12 ẢNH ALL CURE' in source
    assert 'ALL CURE:' in source
    assert "'user_data' / 'all_cure_images'" in (APP / 'spotify_all_cure_market.py').read_text(encoding='utf-8')


def test_v991_workflow_keeps_public_publish_locked_and_supersedes_only_one_v99_node():
    workflow = Path(os.environ['V991_WORKFLOW']).read_text(encoding='utf-8')
    assert 'release-v9.9.1-all-cure-recovery' in workflow
    assert 'gh release create' not in workflow
    assert 'softprops/action-gh-release' not in workflow
    assert 'latest.json' not in workflow
    assert workflow.count('test_all_cure_workflow_is_fail_closed_until_evidence_complete') == 1
    assert '--deselect=' in workflow
