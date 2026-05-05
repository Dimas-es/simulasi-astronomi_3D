"""Banyak asteroid pada sabuk tersebar radius & kecepatan orbit."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import numpy as np

from src.core import config


@dataclass
class Asteroid:
    orbit_radius: float
    orbit_angle: float
    orbit_speed: float
    rot_angle: float
    rot_axis: tuple[float, float, float]
    rot_speed: float
    scale: tuple[float, float, float]


class AsteroidField:
    def __init__(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        self.asteroids: list[Asteroid] = []
        for _ in range(config.ASTEROID_COUNT):
            r = rng.uniform(config.ASTEROID_BELT_R_MIN, config.ASTEROID_BELT_R_MAX)
            self.asteroids.append(
                Asteroid(
                    orbit_radius=r,
                    orbit_angle=rng.uniform(0.0, math.tau),
                    orbit_speed=rng.uniform(
                        config.ASTEROID_ORBIT_SPEED_MIN,
                        config.ASTEROID_ORBIT_SPEED_MAX,
                    ),
                    rot_angle=rng.uniform(0.0, math.tau),
                    rot_axis=(
                        rng.gauss(0.0, 1.0),
                        rng.gauss(0.3, 1.0),
                        rng.gauss(0.0, 1.0),
                    ),
                    rot_speed=rng.uniform(-config.ASTEROID_ROT_SPEED_MAX, config.ASTEROID_ROT_SPEED_MAX),
                    scale=(
                        rng.uniform(config.ASTEROID_SIZE_MIN, config.ASTEROID_SIZE_MAX),
                        rng.uniform(config.ASTEROID_SIZE_MIN, config.ASTEROID_SIZE_MAX),
                        rng.uniform(config.ASTEROID_SIZE_MIN, config.ASTEROID_SIZE_MAX),
                    ),
                )
            )

    def update(self, dt: float) -> None:
        s = config.ORBIT_TIME_SCALE * dt
        for a in self.asteroids:
            a.orbit_angle += a.orbit_speed * s
            a.rot_angle += a.rot_speed * dt

    def world_position(self, a: Asteroid) -> np.ndarray:
        x = a.orbit_radius * math.cos(a.orbit_angle)
        z = a.orbit_radius * math.sin(a.orbit_angle)
        y = 0.15 * math.sin(a.orbit_angle * 2.4 + a.rot_angle * 0.2)
        return np.array([x, y, z], dtype=np.float64)

    def normalize_rot_axis(self, a: Asteroid) -> tuple[float, float, float]:
        ax = np.array(a.rot_axis, dtype=np.float64)
        n = np.linalg.norm(ax)
        if n < 1e-6:
            return (0.0, 1.0, 0.0)
        t = tuple(float(v / n) for v in ax)
        return t
