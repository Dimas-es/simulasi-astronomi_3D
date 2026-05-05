"""Partikel meteor linear yang di-respawn keluar batas."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from src.core import config


@dataclass
class Meteor:
    position: np.ndarray
    velocity: np.ndarray
    trail_prev: np.ndarray


class MeteorSwarm:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed if seed is not None else 91331)
        b = float(config.METEOR_WORLD_BOUND)
        self.trail_len = 3.2
        self.meteors: list[Meteor] = []
        for _ in range(config.METEOR_COUNT):
            self.meteors.append(self._spawn_one(self._rng, b))

    def _spawn_one(self, rng: random.Random, b: float) -> Meteor:
        pos = np.array(
            [
                rng.uniform(-b, b),
                rng.uniform(-b * 0.35, b * 0.35),
                rng.uniform(-b, b),
            ],
            dtype=np.float64,
        )
        sp = rng.uniform(config.METEOR_SPEED_MIN, config.METEOR_SPEED_MAX)
        direction = np.array(
            [rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0), rng.gauss(0.0, 1.0)],
            dtype=np.float64,
        )
        direction /= max(np.linalg.norm(direction), 1e-6)
        vel = direction * sp
        prev = pos - direction * self.trail_len
        return Meteor(position=pos, velocity=vel, trail_prev=prev)

    def update(self, dt: float) -> None:
        b = float(config.METEOR_WORLD_BOUND)
        pad = 22.0
        for m in self.meteors:
            m.position = m.position + m.velocity * dt
            m.trail_prev = m.position - m.velocity / max(np.linalg.norm(m.velocity), 1e-6) * self.trail_len
            p = m.position
            if (
                abs(p[0]) > b + pad
                or abs(p[2]) > b + pad
                or abs(p[1]) > b * 0.5 + pad
            ):
                new = self._spawn_one(self._rng, b)
                m.position[:] = new.position
                m.velocity[:] = new.velocity
                m.trail_prev[:] = new.trail_prev
