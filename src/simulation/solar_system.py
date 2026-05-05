"""Model sistem tata surya sederhana: Matahari + 8 planet, orbit lingkaran."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from src.core import config


@dataclass
class OrbitingBody:
    name: str
    orbit_radius: float
    orbit_speed: float  # radian per detik (skala visual)
    body_radius: float
    rgb: tuple[float, float, float]
    orbit_angle: float = 0.0
    tilt: float = 0.0  # radi


@dataclass
class SolarSystem:
    bodies: list[OrbitingBody]

    @classmethod
    def default_solar_system(cls) -> "SolarSystem":
        # Jarak orbit & kecepatan: semata visual — tidak berskala astronomi nyata.
        defs = [
            ("Merkurius", 4.5, 0.22, 0.35, (0.72, 0.69, 0.65)),
            ("Venus", 6.0, 0.18, 0.55, (0.86, 0.72, 0.52)),
            ("Bumi", 8.0, 0.15, 0.60, (0.2, 0.45, 0.82)),
            ("Mars", 10.0, 0.12, 0.45, (0.73, 0.33, 0.26)),
            ("Jupiter", 14.0, 0.08, 1.35, (0.78, 0.62, 0.45)),
            ("Saturnus", 18.5, 0.06, 1.15, (0.86, 0.77, 0.59)),
            ("Uranus", 23.0, 0.04, 0.85, (0.64, 0.82, 0.91)),
            ("Neptunus", 28.0, 0.035, 0.80, (0.32, 0.45, 0.92)),
        ]
        bodies = [
            OrbitingBody(name=n, orbit_radius=r, orbit_speed=w, body_radius=br, rgb=c)
            for n, r, w, br, c in defs
        ]
        return cls(bodies=bodies)

    def update(self, dt: float) -> None:
        scale = config.ORBIT_TIME_SCALE * dt
        for b in self.bodies:
            b.orbit_angle += b.orbit_speed * scale

    def world_position(self, body: OrbitingBody) -> np.ndarray:
        """Posisi dunia di bidang XZ dengan sedikit kemiringan orbit per planet."""
        x = body.orbit_radius * math.cos(body.orbit_angle)
        z = body.orbit_radius * math.sin(body.orbit_angle)
        y = body.tilt * math.sin(body.orbit_angle * 2.0) * 0.15  # gelombang sangat halus
        return np.array([x, y, z], dtype=np.float64)


SUN_RADIUS = 2.25
SUN_RGB = (1.0, 0.82, 0.24)
