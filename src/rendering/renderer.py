"""Pipeline rendering OpenGL fixed-function: proyeksi, kamera, dan adegan."""

from __future__ import annotations

import math

from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_COLOR_MATERIAL,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_LESS,
    GL_LIGHTING,
    GL_LINE_LOOP,
    GL_MODELVIEW,
    GL_NORMALIZE,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION,
    GL_SRC_ALPHA,
    glBegin,
    glBlendFunc,
    glCallList,
    glClear,
    glClearColor,
    glColor3f,
    glDepthFunc,
    glDisable,
    glEnable,
    glEnd,
    glLoadIdentity,
    glLineWidth,
    glMatrixMode,
    glPopMatrix,
    glPushMatrix,
    glScalef,
    glTranslatef,
    glVertex3f,
    glViewport,
)
from OpenGL.GLU import gluLookAt, gluPerspective

from src.camera.free_roam_camera import FreeRoamCamera
from src.core import config
from src.rendering import lighting
from src.rendering.primitives import build_sphere_display_list
from src.simulation import solar_system as ss


class Renderer:
    def __init__(self) -> None:
        self._width = config.WINDOW_WIDTH
        self._height = config.WINDOW_HEIGHT
        self._sphere_list = 0

    def init_gl(self) -> None:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_NORMALIZE)
        glClearColor(*config.CLEAR_COLOR)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        lighting.configure_lighting()

        self._sphere_list = build_sphere_display_list(1.0)
        self.resize(self._width, self._height)

    def resize(self, width: int, height: int) -> None:
        self._width = max(1, width)
        self._height = max(1, height)
        glViewport(0, 0, self._width, self._height)

    def frame_begin(self, camera: FreeRoamCamera) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self._width / float(self._height)
        gluPerspective(
            camera.fov_degrees,
            aspect,
            config.PROJECTION_NEAR,
            config.PROJECTION_FAR,
        )

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        eye = camera.position
        c = eye + camera.front()
        u = camera.up()

        gluLookAt(
            float(eye[0]),
            float(eye[1]),
            float(eye[2]),
            float(c[0]),
            float(c[1]),
            float(c[2]),
            float(u[0]),
            float(u[1]),
            float(u[2]),
        )

    def _draw_orbit_rings(self, system: ss.SolarSystem) -> None:
        """Lingkaran orbit di bidang XZ untuk tiap planet (tanpa lighting)."""
        glDisable(GL_LIGHTING)
        glLineWidth(float(config.ORBIT_LINE_WIDTH))
        glColor3f(*config.ORBIT_LINE_RGB)

        segments = config.ORBIT_RING_SEGMENTS
        y = float(config.ORBIT_RING_ALTITUDE)
        tau = 2.0 * math.pi

        for body in system.bodies:
            r = body.orbit_radius
            glBegin(GL_LINE_LOOP)
            for i in range(segments):
                theta = tau * float(i) / float(segments)
                x = r * math.cos(theta)
                z = r * math.sin(theta)
                glVertex3f(float(x), y, float(z))
            glEnd()

    def draw_scene(self, system: ss.SolarSystem) -> None:
        """Gambar Matahari, garis orbit, lalu planet (kulembung)."""

        # --- Matahari (pusat 0,0,0 sesuai model simulasi) ---
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glColor3f(*ss.SUN_RGB)
        rs = ss.SUN_RADIUS
        glScalef(rs, rs, rs)
        glCallList(self._sphere_list)
        glPopMatrix()

        self._draw_orbit_rings(system)

        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        lighting.reset_material_white()

        for body in system.bodies:
            pos = system.world_position(body)
            glPushMatrix()
            glTranslatef(float(pos[0]), float(pos[1]), float(pos[2]))
            glColor3f(*body.rgb)
            br = body.body_radius
            glScalef(br, br, br)
            glCallList(self._sphere_list)
            glPopMatrix()

    def dispose(self) -> None:
        from OpenGL.GL import glDeleteLists

        if self._sphere_list:
            glDeleteLists(self._sphere_list, 1)
            self._sphere_list = 0
