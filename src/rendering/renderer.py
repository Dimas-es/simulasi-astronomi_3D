"""Pipeline rendering OpenGL fixed-function: proyeksi, kamera, adegan lengkap."""

from __future__ import annotations

import math

import pygame

from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_COLOR_MATERIAL,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_LINES,
    GL_LIGHTING,
    GL_LINE_LOOP,
    GL_LESS,
    GL_MODELVIEW,
    GL_MODULATE,
    GL_NORMALIZE,
    GL_ONE,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_POLYGON_OFFSET_FILL,
    GL_FRONT,
    GL_PROJECTION,
    GL_REPLACE,
    GL_SPECULAR,
    GL_SRC_ALPHA,
    GL_SHININESS,
    GL_TEXTURE_2D,
    GL_TEXTURE_ENV,
    GL_TEXTURE_ENV_MODE,
    glBegin,
    glBindTexture,
    glBlendFunc,
    glCallList,
    glClear,
    glClearColor,
    glColor3f,
    glColor4f,
    glDepthFunc,
    glDepthMask,
    glDisable,
    glEnable,
    glEnd,
    glLoadIdentity,
    glLineWidth,
    glMaterialf,
    glMaterialfv,
    glMatrixMode,
    glPolygonOffset,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glScalef,
    glTexEnvf,
    glTranslatef,
    glVertex3f,
    glViewport,
)
from OpenGL.GLU import gluLookAt, gluPerspective

from src.camera.free_roam_camera import FreeRoamCamera
from src.core import config
from src.rendering import lighting
from src.rendering.asteroid_mesh import build_octa_rock_display_list
from src.rendering.labels import LabelAtlas
from src.rendering.primitives import (
    build_ring_annulus_display_list,
    build_sphere_display_list,
    delete_display_lists,
)
from src.rendering.textures import TextureAtlas
from src.simulation import solar_system as ss
from src.simulation.asteroid_belt import AsteroidField
from src.simulation.exotic_visitors import ExoticFleet
from src.simulation.meteors import MeteorSwarm


class Renderer:
    def __init__(self, width: int | None = None, height: int | None = None) -> None:
        self._width = width if width is not None else config.WINDOW_WIDTH
        self._height = height if height is not None else config.WINDOW_HEIGHT
        self._sphere_list = 0
        self._rock_list = 0
        self._saturn_ring_lists: list[int] = []
        self._textures: TextureAtlas | None = None
        self._labels: LabelAtlas | None = None

    def init_gl(self, label_font: pygame.font.Font) -> None:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_NORMALIZE)
        glClearColor(*config.CLEAR_COLOR)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        lighting.configure_lighting()

        self._sphere_list = build_sphere_display_list(1.0)
        self._rock_list = build_octa_rock_display_list(jitter=0.14)

        self._saturn_ring_lists = [
            build_ring_annulus_display_list(
                rin,
                rout,
                config.SATURN_RING_SEGMENT_COUNT,
            )
            for (rin, rout, _rgba) in config.SATURN_RING_BANDS
        ]

        self._textures = TextureAtlas() if config.USE_PLANET_TEXTURES else None
        self._labels = LabelAtlas(label_font)
        self.resize(self._width, self._height)

    def preload_textures(self, system: ss.SolarSystem) -> None:
        if self._textures is None or not config.USE_PLANET_TEXTURES:
            return
        atr = self._textures
        atr.preload_key(ss.SUN_TEXTURE_KEY, tuple(float(x) for x in ss.SUN_RGB))
        for b in system.bodies:
            atr.preload_key(b.texture_key, tuple(float(x) for x in b.rgb))
        for sat in system.satellites:
            atr.preload_key(sat.texture_key, tuple(float(x) for x in sat.rgb))

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
        glDisable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
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

    def _draw_textured_sphere(
        self,
        rgb: tuple[float, float, float],
        tex_key: str,
        radius: float,
        textured: bool,
    ) -> None:
        glPushMatrix()
        if textured and config.USE_PLANET_TEXTURES and self._textures is not None:
            glEnable(GL_TEXTURE_2D)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
            tex_id = self._textures.preload_key(tex_key.lower(), tuple(float(x) for x in rgb))
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glColor3f(
                min(1.0, rgb[0] + 0.12),
                min(1.0, rgb[1] + 0.12),
                min(1.0, rgb[2] + 0.12),
            )
        else:
            glDisable(GL_TEXTURE_2D)
            glColor3f(*rgb)
        rr = float(radius)
        glScalef(rr, rr, rr)
        glCallList(self._sphere_list)
        glPopMatrix()

    def _draw_saturn_ring_bands(self, body: ss.OrbitingBody) -> None:
        """Dipanggil dalam matriks: translate orbit; sudah axial tilt × spin aksial."""

        bands = getattr(config, "SATURN_RING_BANDS", ())
        offsets = getattr(config, "SATURN_RING_POLYGON_OFFSET", (-1.2, -3.5))
        if (
            body.texture_key.lower() != "saturn"
            or not self._saturn_ring_lists
            or len(bands) != len(self._saturn_ring_lists)
        ):
            return

        po0, po1 = float(offsets[0]), float(offsets[1])

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPolygonOffset(po0, po1)
        glEnable(GL_POLYGON_OFFSET_FILL)

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)

        glPushMatrix()
        br = float(body.body_radius)
        glScalef(br, br, br)
        for dlist, (_ri, _ro, rgba) in zip(self._saturn_ring_lists, bands, strict=True):
            rr, rg, rb, ra = rgba
            glColor4f(float(rr), float(rg), float(rb), float(ra))
            glCallList(dlist)
        glPopMatrix()

        glEnable(GL_LIGHTING)

        glDisable(GL_POLYGON_OFFSET_FILL)
        glDisable(GL_BLEND)
        lighting.reset_material_white()

    def _draw_sun_textured(self, system: ss.SolarSystem) -> None:
        glDisable(GL_LIGHTING)

        spins = math.degrees(float(system.sun_spin_angle))
        tex_on = config.USE_PLANET_TEXTURES and self._textures is not None

        glPushMatrix()
        glRotatef(spins, 0.0, 1.0, 0.0)
        if tex_on:
            glEnable(GL_TEXTURE_2D)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
            tex_id = self._textures.preload_key(
                ss.SUN_TEXTURE_KEY, tuple(float(x) for x in ss.SUN_RGB)
            )
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glColor3f(1.0, 1.0, 1.0)
        else:
            glDisable(GL_TEXTURE_2D)
            glColor3f(*ss.SUN_RGB)
        rs = float(ss.SUN_RADIUS)
        glScalef(rs, rs, rs)
        glCallList(self._sphere_list)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glDepthMask(False)
        for i, scl in enumerate(config.SUN_HALO_LAYER_SCALES):
            alp = (
                float(config.SUN_HALO_LAYER_ALPHAS[i])
                if i < len(config.SUN_HALO_LAYER_ALPHAS)
                else 0.2
            )
            rgbs = (
                config.SUN_HALO_LAYER_RGB[i]
                if i < len(config.SUN_HALO_LAYER_RGB)
                else (1.0, 0.7, 0.35)
            )
            r0, g0, b0 = float(rgbs[0]), float(rgbs[1]), float(rgbs[2])
            hs = rs * float(scl)
            glPushMatrix()
            glRotatef(spins, 0.0, 1.0, 0.0)
            glColor4f(r0, g0, b0, alp)
            glScalef(hs, hs, hs)
            glCallList(self._sphere_list)
            glPopMatrix()

        glDepthMask(True)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

        glEnable(GL_LIGHTING)

    def _draw_visitors(self, fleet: ExoticFleet | None) -> None:
        if fleet is None:
            return
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        glDisable(GL_TEXTURE_2D)
        spec = [0.88, 0.92, 0.98, 1.0]
        glMaterialfv(GL_FRONT, GL_SPECULAR, spec)
        glMaterialf(GL_FRONT, GL_SHININESS, 96.0)

        scl = float(config.EXOTIC_SCALE)
        for ex in fleet.visitors:
            pos = fleet.position(ex)
            glPushMatrix()
            glTranslatef(float(pos[0]), float(pos[1]), float(pos[2]))
            glRotatef(fleet.facing_yaw(ex), 0.0, 1.0, 0.0)
            glRotatef(-8.5, 1.0, 0.0, 0.0)
            glColor3f(0.62, 0.74, 0.88)

            glPushMatrix()
            glScalef(2.85 * scl, 0.28 * scl, 2.85 * scl)
            glCallList(self._sphere_list)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(0.0, 0.52 * scl, 0.0)
            glScalef(1.12 * scl, 0.78 * scl, 1.12 * scl)
            glColor3f(0.5, 0.65, 0.82)
            glCallList(self._sphere_list)
            glPopMatrix()

            glPopMatrix()

        lighting.reset_material_white()

    def _draw_meteors(self, swarm: MeteorSwarm | None) -> None:
        if swarm is None:
            return
        glDisable(GL_TEXTURE_2D)
        glLineWidth(2.35)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glBegin(GL_LINES)
        for m in swarm.meteors:
            p = m.position
            t = m.trail_prev
            glColor4f(1.0, 0.6, 0.18, 0.88)
            glVertex3f(float(t[0]), float(t[1]), float(t[2]))
            glColor4f(1.0, 0.93, 0.7, 0.98)
            glVertex3f(float(p[0]), float(p[1]), float(p[2]))
        glEnd()
        glDisable(GL_BLEND)

        r = float(config.METEOR_RADIUS)
        for m in swarm.meteors:
            p = m.position
            glPushMatrix()
            glTranslatef(float(p[0]), float(p[1]), float(p[2]))
            glColor3f(0.98, 0.82, 0.42)
            glScalef(r, r, r)
            glCallList(self._sphere_list)
            glPopMatrix()

        glEnable(GL_LIGHTING)

    def _draw_labels(self, camera: FreeRoamCamera, system: ss.SolarSystem) -> None:
        if not config.USE_LABELS or self._labels is None:
            return

        atr = config.LABEL_OFFSET_FACTOR
        self._labels.draw_billboard(ss.SUN_NAME, camera, (0.0, ss.SUN_RADIUS * atr + 0.65, 0.0))

        for b in system.bodies:
            pos = system.world_position(b)
            ly = float(pos[1]) + float(b.body_radius * atr + 0.42)
            self._labels.draw_billboard(b.name, camera, (float(pos[0]), ly, float(pos[2])))

        for s in system.satellites:
            ps = system.world_position_satellite(s)
            ly = float(ps[1]) + float(s.body_radius * atr + 0.32)
            self._labels.draw_billboard(s.name, camera, (float(ps[0]), ly, float(ps[2])))

    def draw_scene(
        self,
        camera: FreeRoamCamera,
        system: ss.SolarSystem,
        asteroid_field: AsteroidField | None,
        meteor_swarm: MeteorSwarm | None,
        exotic_fleet: ExoticFleet | None,
    ) -> None:
        textured = config.USE_PLANET_TEXTURES

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

        self._draw_sun_textured(system)

        self._draw_orbit_rings(system)

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
        lighting.reset_material_white()

        if textured and self._textures is not None:
            glEnable(GL_TEXTURE_2D)

        for body in system.bodies:
            pos = system.world_position(body)
            glPushMatrix()
            glTranslatef(float(pos[0]), float(pos[1]), float(pos[2]))
            glRotatef(float(body.axial_tilt_deg), 1.0, 0.0, 0.0)
            glRotatef(math.degrees(float(body.spin_angle)), 0.0, 1.0, 0.0)
            lighting.apply_planet_material(body.texture_key)
            self._draw_textured_sphere(body.rgb, body.texture_key, body.body_radius, textured)
            lighting.reset_material_white()
            self._draw_saturn_ring_bands(body)
            glPopMatrix()

        for sat in system.satellites:
            ps = system.world_position_satellite(sat)
            glPushMatrix()
            glTranslatef(float(ps[0]), float(ps[1]), float(ps[2]))
            glRotatef(float(sat.axial_tilt_deg), 1.0, 0.0, 0.0)
            glRotatef(math.degrees(float(sat.spin_angle)), 0.0, 1.0, 0.0)
            lighting.apply_planet_material(sat.texture_key)
            self._draw_textured_sphere(sat.rgb, sat.texture_key, sat.body_radius, textured)
            lighting.reset_material_white()
            glPopMatrix()

        glDisable(GL_TEXTURE_2D)

        glEnable(GL_LIGHTING)
        glDisable(GL_TEXTURE_2D)
        if asteroid_field is not None:
            lighting.reset_material_white()
            glColor3f(0.58, 0.52, 0.46)
            for a in asteroid_field.asteroids:
                pw = asteroid_field.world_position(a)
                axis = asteroid_field.normalize_rot_axis(a)
                angle = math.degrees(a.rot_angle)
                glPushMatrix()
                glTranslatef(float(pw[0]), float(pw[1]), float(pw[2]))
                glRotatef(angle, axis[0], axis[1], axis[2])
                glScalef(a.scale[0], a.scale[1], a.scale[2])
                glCallList(self._rock_list)
                glPopMatrix()

        lighting.reset_material_white()

        self._draw_meteors(meteor_swarm)

        self._draw_visitors(exotic_fleet)

        self._draw_labels(camera, system)

    def dispose(self) -> None:
        from OpenGL.GL import glDeleteLists

        if self._textures is not None:
            self._textures.dispose()
            self._textures = None
        if self._labels is not None:
            self._labels.dispose()
            self._labels = None

        if self._saturn_ring_lists:
            delete_display_lists(self._saturn_ring_lists)
            self._saturn_ring_lists.clear()

        if self._sphere_list:
            glDeleteLists(self._sphere_list, 1)
            self._sphere_list = 0
        if self._rock_list:
            glDeleteLists(self._rock_list, 1)
            self._rock_list = 0
