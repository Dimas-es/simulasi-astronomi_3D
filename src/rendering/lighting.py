"""Pencahayaan fixed-function OpenGL sederhana."""

from __future__ import annotations

from OpenGL.GL import (
    GL_AMBIENT,
    GL_COLOR_MATERIAL,
    GL_DIFFUSE,
    GL_FRONT,
    GL_LIGHT0,
    GL_LIGHT_MODEL_AMBIENT,
    GL_LIGHT_MODEL_LOCAL_VIEWER,
    GL_LIGHTING,
    GL_POSITION,
    GL_SPECULAR,
    glColorMaterial,
    glEnable,
    glLightModelf,
    glLightModelfv,
    glLightfv,
    glMaterialfv,
)


def configure_lighting() -> None:
    """Aktifkan satu sumber cahaya (Matahari) + ambient model lembut."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_DIFFUSE)

    ambient = [0.12, 0.12, 0.16, 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)
    glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, 1.0)

    # Cahaya directional (w=0) — stabil di ruang dunia saat MODELVIEW=kamera,
    # hanya mempengaruhi rotasi pandangan tanpa glitch posisi seperti point di origin.
    sun_dir = [0.85, 0.35, 0.42, 0.0]
    glLightfv(GL_LIGHT0, GL_POSITION, sun_dir)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.95, 0.85, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.3, 0.3, 0.28, 1.0])


def reset_material_white() -> None:
    """Material netral untuk objek bersinar dengan glColor."""
    diffuse = [0.85, 0.85, 0.9, 1.0]
    spec = [0.15, 0.15, 0.18, 1.0]
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, spec)
