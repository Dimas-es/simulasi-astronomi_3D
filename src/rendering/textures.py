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
    """RGBA generik (kompatibel lama)."""
    return procedural_rgba_for_key("generic", base_rgb, proc_seed, size)


def procedural_rgba_for_key(
    texture_key: str,
    base_rgb: tuple[float, float, float],
    proc_seed: int,
    size: int,
) -> bytes:
    """Pola procedural per kunci tekstur; baris pertama = bawah tekstur OpenGL."""
    bs = proc_seed + 7919
    denom = float(max(size - 1, 1))
    key = texture_key.lower()
    br, bg, bb = float(base_rgb[0]), float(base_rgb[1]), float(base_rgb[2])
    out = bytearray()

    for row in range(size):
        fy = row / denom
        for col in range(size):
            fx = col / denom
            nx = fx * math.tau - math.pi

            if key == "sun":
                px, py = fx - 0.5, fy - 0.5
                dist = math.hypot(px, py) * 1.9
                n0 = _pseudo_noise(col * 4, row * 4, bs)
                n1 = _pseudo_noise(col * 13, row * 13, bs + 201)
                n2 = _pseudo_noise(col // 3, row // 3, bs + 403)
                gran = n0 * 0.52 + n1 * 0.38 + n2 * 0.10
                faculae = 1.0 + 0.22 * math.sin(fx * 37.8 + fy * 29.2 + n1 * 6.5)
                center = max(0.28, min(1.22, 1.08 - 0.62 * dist * dist))
                v = gran * center * faculae
                r = min(255, int(255 * (0.48 * br + 0.45 * v)))
                g = min(255, int(255 * (0.55 * bg + 0.42 * v * 0.97 + n2 * 0.06)))
                b = min(255, int(255 * (0.35 * bb + 0.20 * v * 0.85)))
                out.extend((r, g, b, 255))

            elif key == "mercury":
                n = _pseudo_noise(col, row, bs)
                n3 = _pseudo_noise(col // 7, row // 7, bs + 1403)
                crater = math.pow(max(1e-6, n), 1.72) * 0.62 + n3 * 0.18
                v = 0.32 + 0.58 * crater + 0.12 * math.sin((fx * 52.3 + fy * 41.0) * math.pi)
                r = int(min(255, br * 255 * v))
                g = int(min(255, bg * 255 * v))
                b = int(min(255, bb * 255 * v))
                out.extend((r, g, b, 255))

            elif key == "venus":
                sw = 0.5 + 0.5 * math.sin(fx * 12.5 + fy * 8.0 + bs * 0.017)
                n = _pseudo_noise(col // 2, row // 2, bs)
                v = 0.73 + 0.19 * sw + 0.09 * n
                tint = math.sin((fx + fy * 3.72) * 17.9) * 0.036
                r = int(min(255, br * 255 * (v + tint)))
                g = int(min(255, bg * 255 * (v * 0.98 + tint)))
                b = int(min(255, bb * 255 * v * 0.91))
                out.extend((r, g, b, 255))

            elif key == "earth":
                n = _pseudo_noise(col, row, bs)
                lc = math.sin((fx + n * 0.43) * 19.7) * math.cos((fy - n * 0.32) * 15.9)
                land_bias = lc * 0.48 + n * 0.38 + 0.16 * math.sin((fx * 44.8 + fy * 29.9) * math.pi)
                if land_bias > 0.05:
                    gscale = min(1.06, 0.58 + land_bias * 0.54)
                    rscale = max(0.15, land_bias * 0.92)
                    bscale = bb * (0.25 + land_bias * 0.06)
                    r = int(min(255, rscale * 255))
                    gm = int(min(255, gscale * 255))
                    bm = int(min(255, bscale * 255))
                    out.extend((r, gm, bm, 255))
                else:
                    ocean = max(0.28, min(1.06, bg * 4.95 + fy * 0.04))
                    rf = max(28, min(110, int(45 + bb * ocean * 90 + n * 22)))
                    gfm = max(58, min(188, int(112 * ocean)))
                    bf = max(138, min(255, int(210 * ocean)))
                    out.extend((rf, gfm, bf, 255))

            elif key == "mars":
                n = _pseudo_noise(col // 4, row // 4, bs)
                ridge = math.sin((fx + n) * math.pi * 22.8) * 0.09
                dusty = br * (0.55 + 0.45 * (_pseudo_noise(col, row, bs + 3)))
                oxide_raw = bg * (0.4 + ridge + 0.35 * math.sin((fy + n) * 31.9))
                oxide = max(0.0, oxide_raw)
                r = max(0, min(255, int(dusty * 255)))
                gm = max(0, min(255, int(oxide * 255)))
                bm = max(28, min(165, int(bb * 165 * math.pow(max(1e-9, float(n)), 0.9))))
                out.extend((r, gm, bm, 255))

            elif key == "jupiter":
                fine = fy + _pseudo_noise(0, int(fy * 400), bs) * 0.08
                bands = math.sin(fine * 44.9 * math.pi) * 0.18 + 0.92
                n = _pseudo_noise(col // 3, row, bs + 551)
                v = bands * (0.74 + n * 0.28)
                r = min(255, int(br * 255 * v * (1.0 + (bands - 0.92) * 0.28)))
                gm = min(255, int(bg * 255 * v * 0.95))
                bm = max(82, min(230, int(bb * 230 * v * 1.06)))
                gdx = fx - 0.52
                gdy = fy - 0.38
                if gdx * gdx * 42.8 + gdy * gdy * 14.9 < 0.036:
                    r = min(255, int(r + 48))
                    gm = max(72, gm - 30)
                    bm = max(64, bm - 55)
                out.extend((r, gm, bm, 255))

            elif key == "saturn":
                bands = math.sin((fy * 62.9 + nx * 0.32) * math.pi) * 0.075 + 0.94
                n = _pseudo_noise(col // 4, row, bs + 701)
                v = bands * (0.78 + 0.22 * n)
                r = min(255, int(br * 255 * v))
                gm = min(255, int(bg * 255 * v * 1.03))
                bm = min(248, max(110, int(bb * 255 * v)))
                out.extend((r, gm, bm, 255))

            elif key == "uranus":
                n = _pseudo_noise(col // 5, row // 5, bs + 1103)
                soft = math.sin((fx * 26.9 + fy * 18.8) * math.pi) * 0.06
                dv = math.sin((fy * 71.9 + fx * fx * -12.9) + n * math.pi)
                streak = dv * n * 0.11
                v = max(0.38, soft + 0.78 + streak)
                rr = max(118, min(255, int(br * 248 * v)))
                gm = max(174, min(255, int(bg * 255 * v)))
                bm = max(214, min(255, int(bb * 255 * v)))
                out.extend((rr, gm, bm, 255))

            elif key == "neptune":
                n = _pseudo_noise(col, row, bs + 2211)
                n9 = _pseudo_noise(col // 8, row // 8, bs + 3333)
                storm_u = fx - 0.42
                storm_v = fy - 0.44
                if storm_u * storm_u * 18.9 + storm_v * storm_v * 14.9 < 0.028:
                    v = max(1.06, min(2.08, n9 * 1.9))
                else:
                    v = 0.71 + n * 0.35 + math.sin((fx * 91.9 + fy * 57.9) * math.pi) * 0.065
                r = max(72, min(255, int(98 + br * v * 85)))
                gm = max(105, min(255, int(112 + bg * v * 120)))
                bm = max(198, min(255, int(185 + bb * v * 68)))
                out.extend((r, gm, bm, 255))

            elif key == "moon":
                n = _pseudo_noise(col // 2, row // 2, bs + 881)
                n2 = _pseudo_noise(col // 11, row // 11, bs + 1205)
                gray = math.pow(n * 0.94 + n2 * 0.28, 1.25)
                v = 0.52 + gray * 0.44 + 0.09 * math.sin((fx + fy + n * 6.88) * 26.88)
                r = int(min(255, br * 255 * v))
                gm = int(min(255, bg * 255 * v))
                bm = int(min(255, bb * 255 * v))
                out.extend((r, gm, bm, 255))

            else:
                n = _pseudo_noise(col, row, bs)
                n2 = _pseudo_noise(col // 5, row // 5, bs + 331)
                v = 0.52 + 0.38 * n + 0.12 * math.sin((fx * 8.3 + fy * 6.1 + n2) * math.pi)
                v = max(0.1, min(1.08, v))
                r = int(min(255, br * 255 * v))
                gm = int(min(255, bg * 255 * v))
                bm = int(min(255, bb * 255 * v))
                out.extend((r, gm, bm, 255))

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

        fid = FILENAME_BY_KEY.get(k, "")
        loaded = _load_disk_rgba(fid) if fid else None
        cap = config.TEXTURE_MAX_EDGE
        proc_size = max(128, min(384, cap * 3 // 4))
        rgb = tuple(float(c) for c in base_rgb)
        proc_seed = (hash(k) ^ int(rgb[0] * 997) ^ int(rgb[2] * 1009)) % 900000 + 101

        if loaded:
            lw, lh, raw = loaded
            upload_texture(tid, lw, lh, raw)
        else:
            raw = procedural_rgba_for_key(k, rgb, proc_seed, proc_size)
            upload_texture(tid, proc_size, proc_size, raw)

        self._tex[k] = tid
        return tid

    def dispose(self) -> None:
        if self._tex:
            glDeleteTextures(list(self._tex.values()))
        self._tex.clear()


def procedural_seed_from_rgb(rgb: tuple[float, float, float]) -> int:
    return int((rgb[0] * 8349 + rgb[1] * 5917 + rgb[2] * 3791) * 1000) % 10_007
