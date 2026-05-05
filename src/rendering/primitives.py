"""Mesh primitif: bola dengan GLU quadric."""

from __future__ import annotations

from OpenGL.GL import GL_COMPILE, glDeleteLists, glEndList, glGenLists, glNewList

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
        # quadric tidak perlu dibebaskan secara eksplisit di binding PyOpenGL umum.
        pass


def delete_display_list(lst: int) -> None:
    if lst:
        glDeleteLists(lst, 1)
