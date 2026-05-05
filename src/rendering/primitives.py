"""Mesh primitif: bola dengan GLU quadric."""

from __future__ import annotations

import math

from OpenGL.GL import (
    GL_COMPILE,
    GL_TRIANGLE_STRIP,
    glBegin,
    glDeleteLists,
    glEnd,
    glEndList,
    glGenLists,
    glNewList,
    glNormal3f,
    glVertex3f,
)

from OpenGL.GLU import (
    GLU_FILL,
    GLU_SMOOTH,
    gluNewQuadric,
    gluQuadricDrawStyle,
    gluQuadricNormals,
    gluSphere,
)


_SPHERE_LAT = 24
_SPHERE_LONG = 24


def build_sphere_display_list(radius: float) -> int:
    """
    Buat display list untuk bola berjari-jari tertentu.
    Pemanggilan harus dalam konteks konteks GL aktif yang sama dengan saat digunakan.
    """
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    try:
        dlist = glGenLists(1)
        glNewList(dlist, GL_COMPILE)
        gluSphere(quadric, radius, _SPHERE_LAT, _SPHERE_LONG)
        glEndList()
        return dlist
    finally:
        pass


def build_ring_annulus_display_list(inner_radius: float, outer_radius: float, segments: int) -> int:
    """Annulus di bidang XZ dengan normal ke +Y."""
    rr_in = float(inner_radius)
    rr_out = float(outer_radius)
    seg = max(8, int(segments))
    tau = 2.0 * math.pi
    dlist = glGenLists(1)
    glNewList(dlist, GL_COMPILE)
    glBegin(GL_TRIANGLE_STRIP)
    glNormal3f(0.0, 1.0, 0.0)
    for i in range(seg + 1):
        theta = tau * float(i) / float(seg)
        ct = math.cos(theta)
        st = math.sin(theta)
        glVertex3f(rr_in * ct, 0.0, rr_in * st)
        glVertex3f(rr_out * ct, 0.0, rr_out * st)
    glEnd()
    glEndList()
    return dlist


def delete_display_list(lst: int) -> None:
    if lst:
        glDeleteLists(lst, 1)


def delete_display_lists(lists: list[int]) -> None:
    """Hapus banyak display list."""
    for lst in lists:
        delete_display_list(lst)
