"""Mesh batu bergelombang sederhana (oktahedron untuk performa baik di fixed GL)."""

from __future__ import annotations

from OpenGL.GL import (
    GL_COMPILE,
    GL_TRIANGLES,
    glBegin,
    glEnd,
    glEndList,
    glGenLists,
    glNewList,
    glNormal3fv,
    glVertex3fv,
)

import numpy as np


def _norm(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else np.array([0.0, 1.0, 0.0], dtype=np.float64)


_TRIS_OCT: list[tuple[int, int, int]] = [
    (0, 2, 4),
    (0, 4, 3),
    (0, 3, 5),
    (0, 5, 2),
    (1, 4, 2),
    (1, 3, 4),
    (1, 5, 3),
    (1, 2, 5),
]


def build_octa_rock_display_list(jitter: float = 0.12, *, rng_seed: int = 731) -> int:
    """
    Bentuk tidak beraturan kecil untuk asteroid: verteks oktahedron + jitter radial.
    """
    raw = np.array(
        [
            [1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, -1.0],
        ],
        dtype=np.float64,
    )
    rng = np.random.default_rng(rng_seed)
    verts_list: list[np.ndarray] = []
    for i in range(len(raw)):
        v = _norm(raw[i])
        r = float(rng.uniform(-jitter, jitter))
        verts_list.append(v * (1.0 + r))
    verts_np = np.array(verts_list, dtype=np.float64)

    dlist_raw = glGenLists(1)
    try:
        dlist = int(dlist_raw)
    except (TypeError, ValueError):
        dlist = int(dlist_raw[0])
    glNewList(dlist, GL_COMPILE)
    glBegin(GL_TRIANGLES)
    for i0, i1, i2 in _TRIS_OCT:
        v0 = verts_np[i0]
        v1 = verts_np[i1]
        v2 = verts_np[i2]
        n = _norm(np.cross(v1 - v0, v2 - v0))
        glNormal3fv(n.astype(np.float32))
        glVertex3fv(v0.astype(np.float32))
        glVertex3fv(v1.astype(np.float32))
        glVertex3fv(v2.astype(np.float32))
    glEnd()
    glEndList()
    return dlist
