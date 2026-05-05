"""Label nama benda: raster font Pygame ke tekstur, lalu quad billboard ke kamera."""

from __future__ import annotations

import math

import pygame

from OpenGL.GL import (
    GL_BLEND,
    GL_CLAMP_TO_EDGE,
    GL_LIGHTING,
    GL_NEAREST,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_POLYGON_OFFSET_FILL,
    GL_QUADS,
    GL_RGBA,
    GL_SRC_ALPHA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glBlendFunc,
    glBegin,
    glColor4f,
    glDeleteTextures,
    glDisable,
    glEnable,
    glEnd,
    glGenTextures,
    glPolygonOffset,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glTexCoord2f,
    glTexImage2D,
    glTexParameteri,
    glTranslatef,
    glVertex3f,
)

from src.camera.free_roam_camera import FreeRoamCamera
from src.core import config


def _gen_tex_int() -> int:
    tid = glGenTextures(1)
    try:
        return int(tid)
    except (TypeError, ValueError):
        return int(tid[0])


def _rgba_png_bytes(surface: pygame.Surface, *, flip_for_gl_bottom_first: bool) -> tuple[int, int, bytes]:
    """RGBA untuk glTexImage2D; flip=True menyelaraskan baris Pygame (atas) ke konvensi GL."""
    w, h = surface.get_size()
    try:
        raw = pygame.image.tobytes(surface, "RGBA", flip_for_gl_bottom_first)
    except TypeError:
        raw = pygame.image.tostring(surface, "RGBA", flip_for_gl_bottom_first)
    return w, h, raw


class LabelAtlas:
    """Satu tekstur OpenGL per string label; ukuran dunia dari LABEL_WORLD_PER_TEX_PX."""

    def __init__(self, font: pygame.font.Font) -> None:
        self._font = font
        self._ids: dict[str, int] = {}
        self._dims: dict[str, tuple[float, float]] = {}

    def ensure(self, text: str) -> None:
        """Bangun tekstur jika belum ada; upload dengan flip baris untuk t memanjang ke atas."""
        if text in self._ids:
            return
        main = tuple(int(c) for c in config.LABEL_TEXT_FG)
        fg = self._font.render(text, False, main)
        sx, sy = fg.get_size()
        pad_x, pad_y = 2, 1
        bw = sx + pad_x * 2
        bh = sy + pad_y * 2
        board = pygame.Surface((bw, bh), pygame.SRCALPHA)
        board.fill((0, 0, 0, 0))
        board.blit(fg, (pad_x, pad_y))

        _, _, raw = _rgba_png_bytes(board, flip_for_gl_bottom_first=True)

        tex = _gen_tex_int()
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, bw, bh, 0, GL_RGBA, GL_UNSIGNED_BYTE, raw)
        self._ids[text] = tex
        scl = float(config.LABEL_WORLD_PER_TEX_PX)
        self._dims[text] = (
            max(1.05, bw * scl),
            max(0.2, bh * scl),
        )

    def draw_billboard(
        self,
        text: str,
        cam: FreeRoamCamera,
        world_xyz: tuple[float, float, float],
    ) -> None:
        """Billboard di bidang XY lokal (+Y naik). Euler menghadap kamera; koordinat u dibalik
        agar teks tidak cermin horizontal setelah yaw+180 derajat.
        """
        self.ensure(text)
        tex = self._ids[text]
        ww, hh = self._dims[text]
        ex, ey, ez = float(cam.position[0]), float(cam.position[1]), float(cam.position[2])
        lx, ly, lz = world_xyz
        dx, dy, dz = ex - lx, ey - ly, ez - lz
        hyp = math.hypot(dx, dz)
        if hyp < 1e-9 and abs(dy) < 1e-9:
            hyp = 1e-9
        yaw_deg = math.degrees(math.atan2(dx, dz))
        pitch_deg = math.degrees(math.atan2(dy, hyp))

        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPolygonOffset(-2.5, -6.0)
        glEnable(GL_POLYGON_OFFSET_FILL)

        glColor4f(1.0, 1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(float(lx), float(ly), float(lz))

        glRotatef(yaw_deg + 180.0, 0.0, 1.0, 0.0)
        glRotatef(-pitch_deg, 1.0, 0.0, 0.0)

        hw, hhh = ww * 0.5, hh * 0.5
        glBegin(GL_QUADS)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-hw, hhh, 0.0)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(hw, hhh, 0.0)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(hw, -hhh, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-hw, -hhh, 0.0)
        glEnd()
        glPopMatrix()

        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)

    def dispose(self) -> None:
        if self._ids:
            glDeleteTextures(list(self._ids.values()))
        self._ids.clear()
        self._dims.clear()
