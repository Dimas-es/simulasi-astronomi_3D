"""Game loop, inisialisasi Pygame + OpenGL, dan overlay HUD."""

from __future__ import annotations

import sys

import pygame
from OpenGL.GL import (
    GL_BLEND,
    GL_CLAMP_TO_EDGE,
    GL_COLOR_MATERIAL,
    GL_DEPTH_TEST,
    GL_LINEAR,
    GL_LIGHTING,
    GL_MODELVIEW,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION,
    GL_QUADS,
    GL_REPLACE,
    GL_RGBA,
    GL_SRC_ALPHA,
    GL_TEXTURE_2D,
    GL_TEXTURE_ENV,
    GL_TEXTURE_ENV_MODE,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBegin,
    glBindTexture,
    glBlendFunc,
    glColor4f,
    glDeleteTextures,
    glDisable,
    glEnable,
    glEnd,
    glGenTextures,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glPopMatrix,
    glPushMatrix,
    glTexCoord2f,
    glTexEnvf,
    glTexImage2D,
    glTexParameteri,
    glVertex2f,
    glViewport,
)

from src.camera.free_roam_camera import FreeRoamCamera
from src.core import config
from src.input.input_handler import InputHandler
from src.rendering.renderer import Renderer
from src.simulation.asteroid_belt import AsteroidField
from src.simulation.exotic_visitors import ExoticFleet
from src.simulation.meteors import MeteorSwarm
from src.simulation.solar_system import SolarSystem


def _fit_inside_cap(width: int, height: int) -> tuple[int, int]:
    """Kecilkan secara seragam jika lebih besar dari WINDOW_INIT_MAX_* (pertahankan aspect)."""
    cap_w = int(config.WINDOW_INIT_MAX_WIDTH)
    cap_h = int(config.WINDOW_INIT_MAX_HEIGHT)
    if cap_w <= 0 or cap_h <= 0:
        return width, height
    if width <= cap_w and height <= cap_h:
        return width, height
    scale = min(cap_w / float(width), cap_h / float(height))
    fit_w = max(640, int(width * scale))
    fit_h = max(480, int(height * scale))
    return fit_w, fit_h


def _initial_window_size() -> tuple[int, int]:
    """Ukuran jendela pertama: resolusi desktop utama (Pygame) atau fallback config."""
    fw, fh = int(config.WINDOW_WIDTH), int(config.WINDOW_HEIGHT)
    min_w, min_h = 640, 480
    if not config.WINDOW_MATCH_DESKTOP:
        return max(min_w, fw), max(min_h, fh)
    info = pygame.display.Info()
    cw, ch = int(info.current_w), int(info.current_h)
    if cw > 0 and ch > 0:
        uw, uh = max(min_w, cw), max(min_h, ch)
        return _fit_inside_cap(uw, uh)
    return max(min_w, fw), max(min_h, fh)


def _display_pixels() -> tuple[int, int]:
    """Lebar/tinggi buffer tampilan untuk GL (HiDPI bisa beda dari logical size)."""
    try:
        ww, wh = pygame.display.get_window_size()
        if ww > 0 and wh > 0:
            return ww, wh
    except (AttributeError, TypeError, pygame.error):
        pass
    surf = pygame.display.get_surface()
    if surf is not None:
        return surf.get_width(), surf.get_height()
    return int(config.WINDOW_WIDTH), int(config.WINDOW_HEIGHT)


def _texture_id(tex) -> int:
    """Normalisasi nilai kembalian glGenTextures menjadi int."""
    try:
        return int(tex)
    except (TypeError, ValueError):
        return int(tex[0])


def _draw_hud_overlay(
    screen_width: int,
    screen_height: int,
    font: pygame.font.Font,
    lines: list[str],
    texture_holder: list[int],
) -> None:
    """Gambar panel teks di pojok kiri atas dengan blending alpha."""
    line_h = font.get_linesize()
    pad = 8
    max_w = 0
    for line in lines:
        max_w = max(max_w, font.size(line)[0])
    panel_w = max(max_w + pad * 2, 280)
    panel_h = len(lines) * line_h + pad * 2

    surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    surf.fill((8, 10, 24, 200))
    y = pad
    for line in lines:
        text_surf = font.render(line, True, (235, 238, 252))
        surf.blit(text_surf, (pad, y))
        y += line_h

    w, h = surf.get_size()
    try:
        raw = pygame.image.tobytes(surf, "RGBA", True)
    except TypeError:
        raw = pygame.image.tostring(surf, "RGBA", True)  # pygame < 2 idiom

    if not texture_holder:
        texture_holder.append(_texture_id(glGenTextures(1)))
    tid = texture_holder[0]

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tid)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, raw)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_COLOR_MATERIAL)

    # draw_scene memakai GL_MODULATE; tanpa REPLACE + warna putih HUD jadi kusam / seolah «terpotong».
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glColor4f(1.0, 1.0, 1.0, 1.0)

    glViewport(0, 0, int(screen_width), int(screen_height))

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0.0, float(screen_width), float(screen_height), 0.0, -1.0, 1.0)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    margin = 12.0
    x0, y0 = margin, margin
    x1, y1 = x0 + float(w), y0 + float(h)

    # Koordinat tekstur: v=0 dasar, v=1 atas (OpenGL). Pojok kiri atas layar memakai v=1
    # agar baris pertama Pygame (atas) tidak tampil terbalik.
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(x0, y0)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(x1, y0)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(x1, y1)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(x0, y1)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glDisable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_COLOR_MATERIAL)


def run_app() -> None:
    pygame.init()
    pygame.display.set_caption(config.WINDOW_TITLE)

    flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
    init_w, init_h = _initial_window_size()
    pygame.display.set_mode((init_w, init_h), flags)

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    clock = pygame.time.Clock()
    camera = FreeRoamCamera.create_default()
    solar = SolarSystem.default_solar_system()
    asteroid_field = AsteroidField(seed=2026)
    meteor_swarm = MeteorSwarm(seed=904)
    exotic_fleet = ExoticFleet()
    inputs = InputHandler(mouse_grabbed=True, video_flags=flags)

    aw, ah = _display_pixels()
    renderer = Renderer(width=aw, height=ah)

    pygame.font.init()
    label_font = pygame.font.SysFont("dejavusans", config.LABEL_FONT_PT, bold=True)

    renderer.init_gl(label_font)
    renderer.preload_textures(solar)

    hud_font = pygame.font.Font(None, 22)
    hud_texture: list[int] = []
    fps_smooth = 0.0
    running = True

    try:
        while running:
            dt_ms = clock.tick(120)
            dt = max(dt_ms, 1) / 1000.0
            fps_instant = 1.0 / dt if dt > 0 else 0.0
            fps_smooth = fps_smooth * 0.9 + fps_instant * 0.1 if fps_smooth > 0 else fps_instant

            running = inputs.process_events()
            inputs.apply_to_camera(camera, dt)
            solar.update(dt)
            asteroid_field.update(dt)
            meteor_swarm.update(dt)
            exotic_fleet.update(dt)

            w, h = _display_pixels()
            renderer.resize(w, h)

            renderer.frame_begin(camera)
            renderer.draw_scene(camera, solar, asteroid_field, meteor_swarm, exotic_fleet)

            hud_lines = [
                "Simulasi Astronomi 3D — kontrol",
                "W / S: maju / mundur",
                "A / D: geser kiri / kanan",
                "Spasi / Ctrl: naik / turun",
                "Mouse: putar pandangan (kursor ditangkap)",
                "Scroll: zoom (persempit / perlebar pandangan)",
                "Esc: keluar",
                f"FOV: {camera.fov_degrees:.1f}° | FPS: {fps_smooth:.0f}",
            ]
            _draw_hud_overlay(w, h, hud_font, hud_lines, hud_texture)

            pygame.display.flip()
    finally:
        if hud_texture:
            glDeleteTextures([hud_texture[0]])
        renderer.dispose()
        pygame.quit()

    sys.exit(0)
