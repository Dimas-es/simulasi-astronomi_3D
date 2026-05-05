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
    tilt: float = 0.0  # radian — getaran orbit kecil (bukan kemiringan sumbu)
    axial_tilt_deg: float = 0.0  # kemiringan sumbu visual (putar sekitar +X sebelum spin)
    spin_speed: float = 0.3  # radian per detik dunia (permukaan berputar)
    spin_angle: float = 0.0


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
    axial_tilt_deg: float = 0.0
    spin_speed: float = 0.2
    spin_angle: float = 0.0


@dataclass
class SolarSystem:
    bodies: list[OrbitingBody]
    satellites: list[Satellite] = field(default_factory=list)
    sun_spin_speed: float = 0.085
    sun_spin_angle: float = 0.0

    @classmethod
    def default_solar_system(cls) -> "SolarSystem":
        defs: list[
            tuple[str, float, float, float, tuple[float, float, float], str, float, float]
        ] = [
            ("Merkurius", 4.5, 0.22, 0.35, (0.72, 0.69, 0.65), "mercury", 0.034, 0.18),
            ("Venus", 6.0, 0.18, 0.55, (0.86, 0.72, 0.52), "venus", -177.3, -0.07),
            ("Bumi", 8.0, 0.15, 0.60, (0.2, 0.45, 0.82), "earth", 23.44, 0.42),
            ("Mars", 10.0, 0.12, 0.45, (0.73, 0.33, 0.26), "mars", 25.19, 0.41),
            ("Jupiter", 14.0, 0.08, 1.35, (0.78, 0.62, 0.45), "jupiter", 3.13, 0.88),
            ("Saturnus", 18.5, 0.06, 1.15, (0.86, 0.77, 0.59), "saturn", 26.73, 0.82),
            ("Uranus", 23.0, 0.04, 0.85, (0.64, 0.82, 0.91), "uranus", 97.77, -0.55),
            ("Neptunus", 28.0, 0.035, 0.80, (0.32, 0.45, 0.92), "neptune", 28.32, 0.62),
        ]
        bodies = [
            OrbitingBody(
                name=n,
                orbit_radius=r,
                orbit_speed=w,
                body_radius=br,
                rgb=c,
                texture_key=tk,
                axial_tilt_deg=tdeg,
                spin_speed=ssp,
            )
            for (n, r, w, br, c, tk, tdeg, ssp) in defs
        ]
        moon = Satellite(
            name="Bulan",
            parent_name="Bumi",
            orbit_radius=0.65,
            orbit_speed=1.4,
            body_radius=0.16,
            rgb=(0.55, 0.55, 0.58),
            texture_key="moon",
            axial_tilt_deg=6.7,
            spin_speed=0.14,
        )
        return cls(bodies=bodies, satellites=[moon])

    def update(self, dt: float) -> None:
        scale = config.ORBIT_TIME_SCALE * dt
        orbit_dt = dt
        tau = math.tau
        self.sun_spin_angle = (self.sun_spin_angle + self.sun_spin_speed * orbit_dt) % tau

        for b in self.bodies:
            b.orbit_angle += b.orbit_speed * scale
            b.spin_angle = (b.spin_angle + b.spin_speed * orbit_dt) % tau
        for s in self.satellites:
            s.orbit_angle += s.orbit_speed * scale
            s.spin_angle = (s.spin_angle + s.spin_speed * orbit_dt) % tau

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
