import binascii
import struct
import zlib
from pathlib import Path
import pytest
from spotify_all_cure_assets import REQUIRED_ALL_CURE_ASSETS, SpotifyAllCureAssetGateway

def chunk(kind,data):
    body=kind+data
    return struct.pack('>I',len(data))+body+struct.pack('>I',binascii.crc32(body)&0xffffffff)

def tiny_png():
    sig=b'\x89PNG\r\n\x1a\n'; ihdr=struct.pack('>IIBBBBB',1,1,8,0,0,0,0)
    return sig+chunk(b'IHDR',ihdr)+chunk(b'IDAT',zlib.compress(b'\x00\x00'))+chunk(b'IEND',b'')

def seed_all(root:Path):
    root.mkdir(parents=True,exist_ok=True)
    for name in REQUIRED_ALL_CURE_ASSETS: (root/name).write_bytes(tiny_png())

def test_all_required_valid_pngs_are_ready(tmp_path):
    seed_all(tmp_path); status=SpotifyAllCureAssetGateway(tmp_path).validate()
    assert status.ready and status.missing==() and status.invalid==()

def test_missing_or_corrupt_png_blocks(tmp_path):
    seed_all(tmp_path); (tmp_path/REQUIRED_ALL_CURE_ASSETS[2]).unlink()
    status=SpotifyAllCureAssetGateway(tmp_path).validate(); assert not status.ready
    assert status.missing==(REQUIRED_ALL_CURE_ASSETS[2],)
    seed_all(tmp_path); (tmp_path/REQUIRED_ALL_CURE_ASSETS[5]).write_bytes(b'not-a-png')
    status=SpotifyAllCureAssetGateway(tmp_path).validate(); assert not status.ready
    assert status.invalid==(REQUIRED_ALL_CURE_ASSETS[5],)

def test_crc_or_idat_corruption_blocks(tmp_path):
    seed_all(tmp_path); p=tmp_path/REQUIRED_ALL_CURE_ASSETS[0]; raw=bytearray(p.read_bytes()); raw[-5]^=1; p.write_bytes(raw)
    assert not SpotifyAllCureAssetGateway(tmp_path).validate().ready

def test_path_for_rejects_unknown_extension_and_traversal(tmp_path):
    g=SpotifyAllCureAssetGateway(tmp_path); assert g.path_for('empty.png')==tmp_path/'empty.png'
    for bad in ('other.png','empty.jpg','../empty.png','x/empty.png'):
        with pytest.raises(ValueError): g.path_for(bad)
