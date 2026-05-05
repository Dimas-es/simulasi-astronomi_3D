"""Muat tekstur permukaan bola (file atau fallback procedural)."""

from __future__ import annotations

import hashlib
import math
import struct
from pathlib import Path
from typing import Optional

from OpenGL.GL import (
    GL_CLAMP_TO_EDGE,
    GL_LINEAR,
    GL_LINEAR_MIPMAP_LINEAR,
    GL_RGBA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glDeleteTextures,
    glGenerateMipmap,
    glGenTextures,
    glTexImage2D,
    glTexParameteri,
)

try:
    from PIL import Image
except ImportError:
    Image = None  # type: ignore

from src.core import config

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_TEXTURE_DIR = _PROJECT_ROOT / config.ASSETS_TEXTURES_SUBDIR

FILENAME_BY_KEY: dict[str, str] = {
    "sun": "sun.jpg",
    "mercury": "mercury.jpg",
    "venus": "venus.jpg",
    "earth": "earth.jpg",
    "mars": "mars.jpg",
    "jupiter": "jupiter.jpg",
    "saturn": "saturn.jpg",
    "uranus": "uranus.jpg",
    "neptune": "neptune.jpg",
    "moon": "moon.jpg",
    "asteroid": "asteroid.jpg",
}


def _pseudo_noise(x: int, y: int, seed: int) -> float:
    """Noise deterministik; operand di-mask 32-bit agar struct.pack tidak overflow."""
    a = (x * 374761393 + seed * 7919) & 0xFFFFFFFF
    b = (y * 668265263 + seed * 1337) & 0xFFFFFFFF
    c = (((x ^ (y << 16)) ^ (seed << 8)) & 0xFFFFFFFF) ^ 0x9E3779B9
    buf = struct.pack("<III", a, b, c)
    h = int(hashlib.md5(buf).hexdigest()[:8], 16)
    return (h & 0xFFFF) / 65535.0


def procedural_rgba_bytes(
    base_rgb: tuple[float, float, float],
    proc_seed: int,
    size: int,
) -> bytes:
    """RGBA row-major cocok untuk glTexImage2D (baris pertama = bawah teksur)."""
    out = bytearray()
    bs = proc_seed + 7919
    for row in range(size):
        fy = row / float(max(size - 1, 1))
        for col in range(size):
            fx = col / float(max(size - 1, 1))
            n = _pseudo_noise(col, row, bs)
            n2 = _pseudo_noise(col // 5, row // 5, bs + 331)
            v = 0.52 + 0.38 * n + 0.12 * math.sin((fx * 8.3 + fy * 6.1 + n2) * math.pi)
            v = max(0.1, min(1.08, v))
            r = int(min(255, base_rgb[0] * 255 * v))
            g = int(min(255, base_rgb[1] * 255 * v))
            b = int(min(255, base_rgb[2] * 255 * v))
            out.extend((r, g, b, 255))
    return bytes(out)


def _load_disk_rgba(fname: str) -> Optional[tuple[int, int, bytes]]:
    if Image is None:
        return None
    path = _TEXT_DIR_PATH(fname)
    if not path.is_file():
        return None
    try:
        img = Image.open(path).convert("RGBA")
        w0, h0 = img.size
        mx = config.TEXTURE_MAX_EDGE
        if max(w0, h0) > mx:
            scale = mx / float(max(w0, h0))
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS  # type: ignore[attr-defined]
            img = img.resize(
                (max(2, int(w0 * scale)), max(2, int(h0 * scale))),
                resample,
            )
        w, h = img.size
        raw = img.transpose(Image.FLIP_TOP_BOTTOM).tobytes()
        return w, h, raw
    except OSError:
        return None


def _TEXT_DIR_PATH(fname: str) -> Path:
    return _TEXTURE_DIR / fname


def upload_texture(tex_id: int, w: int, h: int, raw_rgba: bytes) -> None:
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, raw_rgba)
    try:
        glGenerateMipmap(GL_TEXTURE_2D)
    except Exception:
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)


class TextureAtlas:
    """Satu tekstur OpenGL per kunci pemetaan nama."""

    def __init__(self) -> None:
        self._tex: dict[str, int] = {}

    def preload_key(self, key: str, base_rgb: tuple[float, float, float]) -> int:
        """Ambil atau buat tekstur untuk given key."""
        k = key.lower()
        if k in self._tex:
            return self._tex[k]

        tex_raw = glGenTextures(1)
        try:
            tid = int(tex_raw)
        except (TypeError, ValueError):
            tid = int(tex_raw[0])

        fid = FILENAME_BY_KEY.get(key.lower(), "")
        loaded = _load_disk_rgba(fid) if fid else None
        proc_size = max(96, min(256, config.TEXTURE_MAX_EDGE // 2))
        rgb = tuple(float(c) for c in base_rgb)
        proc_seed = (hash(key) ^ int(rgb[0] * 997) ^ int(rgb[2] * 1009)) % 900000 + 101

        if loaded:
            lw, lh, raw = loaded
            upload_texture(tid, lw, lh, raw)
        else:
            raw = procedural_rgba_bytes(rgb, proc_seed, proc_size)
            upload_texture(tid, proc_size, proc_size, raw)

        self._tex[k] = tid
        return tid

    def dispose(self) -> None:
        if self._tex:
            glDeleteTextures(list(self._tex.values()))
        self._tex.clear()


def procedural_seed_from_rgb(rgb: tuple[float, float, float]) -> int:
    return int((rgb[0] * 8349 + rgb[1] * 5917 + rgb[2] * 3791) * 1000) % 10_007
