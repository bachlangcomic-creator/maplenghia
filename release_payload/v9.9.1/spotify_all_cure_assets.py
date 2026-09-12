from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import binascii
import struct
import zlib
import shutil
import uuid

REQUIRED_ALL_CURE_ASSETS = (
    'empty.png', 'npc_all_cure.png', 'all_cure_line.png', 'confirm_all_cure.png',
    'buy_all_cure.png', 'finish_buying.png', 'shop.png', 'exit.png',
    'all_cure_pots.png', 'set_sell_item.png', 'confirm_set_item_to_sell.png',
    'complete_set_item.png',
)

_PNG_SIG = b'\x89PNG\r\n\x1a\n'


@dataclass(frozen=True)
class AllCureAssetStatus:
    ready: bool
    missing: tuple[str, ...]
    invalid: tuple[str, ...]


def _valid_png(raw: bytes) -> bool:
    if not raw.startswith(_PNG_SIG):
        return False
    pos = len(_PNG_SIG)
    ihdr = None
    idat = bytearray()
    saw_iend = False
    try:
        while pos < len(raw):
            if pos + 12 > len(raw):
                return False
            length = struct.unpack('>I', raw[pos:pos + 4])[0]
            kind = raw[pos + 4:pos + 8]
            data_start = pos + 8
            data_end = data_start + length
            crc_end = data_end + 4
            if crc_end > len(raw):
                return False
            data = raw[data_start:data_end]
            want_crc = struct.unpack('>I', raw[data_end:crc_end])[0]
            got_crc = binascii.crc32(kind + data) & 0xFFFFFFFF
            if got_crc != want_crc:
                return False
            if kind == b'IHDR':
                if ihdr is not None or length != 13:
                    return False
                width, height, bit_depth, color_type, comp, filt, interlace = struct.unpack('>IIBBBBB', data)
                if width <= 0 or height <= 0:
                    return False
                if bit_depth not in (1, 2, 4, 8, 16):
                    return False
                if color_type not in (0, 2, 3, 4, 6):
                    return False
                if comp != 0 or filt != 0 or interlace not in (0, 1):
                    return False
                ihdr = (width, height)
            elif kind == b'IDAT':
                idat.extend(data)
            elif kind == b'IEND':
                if length != 0:
                    return False
                saw_iend = True
                pos = crc_end
                break
            pos = crc_end
        if ihdr is None or not idat or not saw_iend:
            return False
        if pos != len(raw):
            return False
        zlib.decompress(bytes(idat))
        return True
    except (ValueError, struct.error, zlib.error):
        return False


class SpotifyAllCureAssetGateway:
    def __init__(self, asset_dir):
        self.asset_dir = Path(asset_dir)

    def path_for(self, name: str) -> Path:
        if name not in REQUIRED_ALL_CURE_ASSETS:
            raise ValueError(f'unknown All Cure asset: {name!r}')
        if Path(name).name != name or Path(name).suffix.lower() != '.png':
            raise ValueError(f'invalid All Cure asset path: {name!r}')
        return self.asset_dir / name

    def validate(self) -> AllCureAssetStatus:
        missing = []
        invalid = []
        for name in REQUIRED_ALL_CURE_ASSETS:
            path = self.path_for(name)
            if not path.is_file():
                missing.append(name)
                continue
            try:
                raw = path.read_bytes()
            except OSError:
                invalid.append(name)
                continue
            if not _valid_png(raw):
                invalid.append(name)
        return AllCureAssetStatus(not missing and not invalid, tuple(missing), tuple(invalid))

    def import_from_directory(self, source_dir) -> AllCureAssetStatus:
        source_dir = Path(source_dir)
        source_gateway = SpotifyAllCureAssetGateway(source_dir)
        source_status = source_gateway.validate()
        if not source_status.ready:
            return source_status

        try:
            if source_dir.resolve() == self.asset_dir.resolve():
                return self.validate()
        except OSError:
            pass

        parent = self.asset_dir.parent
        parent.mkdir(parents=True, exist_ok=True)
        token = uuid.uuid4().hex
        stage = parent / f'.all_cure_images.stage.{token}'
        backup = parent / f'.all_cure_images.backup.{token}'
        moved_old = False
        try:
            stage.mkdir(parents=False, exist_ok=False)
            for name in REQUIRED_ALL_CURE_ASSETS:
                shutil.copy2(source_gateway.path_for(name), stage / name)
            staged_status = SpotifyAllCureAssetGateway(stage).validate()
            if not staged_status.ready:
                return staged_status

            if self.asset_dir.exists():
                self.asset_dir.rename(backup)
                moved_old = True
            stage.rename(self.asset_dir)
            if backup.exists():
                shutil.rmtree(backup)
            return self.validate()
        except OSError:
            if self.asset_dir.exists() and moved_old and backup.exists():
                shutil.rmtree(self.asset_dir, ignore_errors=True)
            if moved_old and backup.exists() and not self.asset_dir.exists():
                try:
                    backup.rename(self.asset_dir)
                except OSError:
                    pass
            return self.validate()
        finally:
            if stage.exists():
                shutil.rmtree(stage, ignore_errors=True)
            if backup.exists() and self.asset_dir.exists():
                shutil.rmtree(backup, ignore_errors=True)
