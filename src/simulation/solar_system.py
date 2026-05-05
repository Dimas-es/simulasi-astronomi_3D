"""Model sistem tata surya: planet, satelit Bulan, konsanta Matahari."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from src.core import config


SUN_NAME = "Matahari"
SUN_RADIUS = 2.25
SUN_RGB = (1.0, 0.82, 0.24)
SUN_TEXTURE_KEY = "sun"


@dataclass
class OrbitingBody:
    name: str
    orbit_radius: float
    orbit_speed: float  # radian per detik (skala visual)
    body_radius: float
    rgb: tuple[float, float, float]
    texture_key: str
    orbit_angle: float = 0.0
    tilt: float = 0.0  # radian


@dataclass
class Satellite:
    """Orbit relatif ke pusat parent (biasanya planet)."""

    name: str
    parent_name: str
    orbit_radius: float
    orbit_speed: float
    body_radius: float
    rgb: tuple[float, float, float]
    texture_key: str = "moon"
    orbit_angle: float = 0.0


@dataclass
class SolarSystem:
    bodies: list[OrbitingBody]
    satellites: list[Satellite] = field(default_factory=list)

    @classmethod
    def default_solar_system(cls) -> "SolarSystem":
        defs: list[tuple[str, float, float, float, tuple[float, float, float], str]] = [
            ("Merkurius", 4.5, 0.22, 0.35, (0.72, 0.69, 0.65), "mercury"),
            ("Venus", 6.0, 0.18, 0.55, (0.86, 0.72, 0.52), "venus"),
            ("Bumi", 8.0, 0.15, 0.60, (0.2, 0.45, 0.82), "earth"),
            ("Mars", 10.0, 0.12, 0.45, (0.73, 0.33, 0.26), "mars"),
            ("Jupiter", 14.0, 0.08, 1.35, (0.78, 0.62, 0.45), "jupiter"),
            ("Saturnus", 18.5, 0.06, 1.15, (0.86, 0.77, 0.59), "saturn"),
            ("Uranus", 23.0, 0.04, 0.85, (0.64, 0.82, 0.91), "uranus"),
            ("Neptunus", 28.0, 0.035, 0.80, (0.32, 0.45, 0.92), "neptune"),
        ]
        bodies = [
            OrbitingBody(
                name=n,
                orbit_radius=r,
                orbit_speed=w,
                body_radius=br,
                rgb=c,
                texture_key=tk,
            )
            for n, r, w, br, c, tk in defs
        ]
        moon = Satellite(
            name="Bulan",
            parent_name="Bumi",
            orbit_radius=0.65,
            orbit_speed=1.4,
            body_radius=0.16,
            rgb=(0.55, 0.55, 0.58),
            texture_key="moon",
        )
        return cls(bodies=bodies, satellites=[moon])

    def update(self, dt: float) -> None:
        scale = config.ORBIT_TIME_SCALE * dt
        for b in self.bodies:
            b.orbit_angle += b.orbit_speed * scale
        for s in self.satellites:
            s.orbit_angle += s.orbit_speed * scale

    def world_position(self, body: OrbitingBody) -> np.ndarray:
        """Posisi dunia di bidang XZ dengan gangguan tilt kecil."""
        x = body.orbit_radius * math.cos(body.orbit_angle)
        z = body.orbit_radius * math.sin(body.orbit_angle)
        y = body.tilt * math.sin(body.orbit_angle * 2.0) * 0.15
        return np.array([x, y, z], dtype=np.float64)

    def body_by_name(self, name: str) -> OrbitingBody:
        for b in self.bodies:
            if b.name == name:
                return b
        raise KeyError(name)

    def world_position_satellite(self, sat: Satellite) -> np.ndarray:
        parent = self.body_by_name(sat.parent_name)
        p = self.world_position(parent)
        x = sat.orbit_radius * math.cos(sat.orbit_angle)
        z = sat.orbit_radius * math.sin(sat.orbit_angle)
        y = 0.05 * math.sin(sat.orbit_angle * 3.0)
        return p + np.array([x, y, z], dtype=np.float64)
