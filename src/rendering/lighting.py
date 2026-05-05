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
    GL_SHININESS,
    GL_SPECULAR,
    glColorMaterial,
    glEnable,
    glLightModelf,
    glLightModelfv,
    glLightfv,
    glMaterialf,
    glMaterialfv,
)


def configure_lighting() -> None:
    """Aktifkan GL_LIGHT0 + ambient model.

    Arah cahaya memakai koordinat homogen w=0 (directional), sehingga tetap
    konsisten di ruang dunia saat matriks MODELVIEW mengikuti kamera.
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_DIFFUSE)

    ambient = [0.12, 0.12, 0.16, 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)
    glLightModelf(GL_LIGHT_MODEL_LOCAL_VIEWER, 1.0)

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
    glMaterialf(GL_FRONT, GL_SHININESS, 32.0)


def apply_planet_material(texture_key: str) -> None:
    """Specular / shininess bergantung kelas permukaan (batuan vs es vs gas)."""
    k = texture_key.lower()
    diffuse = [0.92, 0.92, 0.95, 1.0]
    if k in ("mercury", "mars", "moon"):
        spec = [0.065, 0.065, 0.068, 1.0]
        shin = 14.0
    elif k in ("venus", "earth"):
        spec = [0.09, 0.09, 0.096, 1.0]
        shin = 26.0
    elif k in ("uranus", "neptune"):
        spec = [0.34, 0.36, 0.42, 1.0]
        shin = 88.0
    elif k in ("jupiter", "saturn"):
        spec = [0.05, 0.048, 0.046, 1.0]
        shin = 18.0
    else:
        spec = [0.1, 0.11, 0.12, 1.0]
        shin = 22.0
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, spec)
    glMaterialf(GL_FRONT, GL_SHININESS, shin)
