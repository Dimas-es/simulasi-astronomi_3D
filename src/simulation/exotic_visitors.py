"""Objek asing bergerak lintasan flyby elips / harmonik."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from src.core import config


@dataclass
class ExoticVisitor:
    """Satu \"UFO\" mengitari sumbu Y dengan elips horizontal + goyangan vertikal."""

    phase_offset: float
    radius: float
    angular_speed: float
    bob_amplitude: float
    bob_freq: float


class ExoticFleet:
    def __init__(self) -> None:
        self.visitors: list[ExoticVisitor] = []
        for i in range(config.EXOTIC_VISITOR_COUNT):
            off = (math.tau / max(config.EXOTIC_VISITOR_COUNT, 1)) * i + 1.7
            self.visitors.append(
                ExoticVisitor(
                    phase_offset=off,
                    radius=config.EXOTIC_FLYBY_RADIUS * (0.88 + 0.12 * i),
                    angular_speed=config.EXOTIC_FLYBY_ANGULAR_SPEED * (0.9 + 0.08 * i),
                    bob_amplitude=4.5 + 1.2 * i,
                    bob_freq=0.22 + 0.05 * i,
                )
            )
        self.global_t = 0.0

    def update(self, dt: float) -> None:
        self.global_t += dt

    def position(self, ex: ExoticVisitor) -> np.ndarray:
        t = self.global_t * ex.angular_speed + ex.phase_offset
        x = ex.radius * math.cos(t)
        z = ex.radius * math.sin(t) * 0.85
        y = 12.0 + ex.bob_amplitude * math.sin(t * ex.bob_freq * 2.0)
        return np.array([x, y, z], dtype=np.float64)

    def facing_yaw(self, ex: ExoticVisitor) -> float:
        t = self.global_t * ex.angular_speed + ex.phase_offset
        return math.degrees(t) + 90.0
