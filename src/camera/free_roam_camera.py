"""Kamera navigasi free-roam (FPS-style) dengan yaw/pitch dan zoom FOV."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from src.core import config


@dataclass
class FreeRoamCamera:
    """Kamera dengan posisi, orientasi yaw/pitch, dan field of view untuk zoom."""

    position: np.ndarray
    yaw: float
    pitch: float
    fov_degrees: float

    @classmethod
    def create_default(cls) -> "FreeRoamCamera":
        pos = np.array([0.0, 10.0, 35.0], dtype=np.float64)
        yaw = math.radians(-90.0)
        pitch = math.radians(-12.0)
        return cls(
            position=pos,
            yaw=yaw,
            pitch=pitch,
            fov_degrees=config.CAMERA_FOV_DEFAULT,
        )

    def front(self) -> np.ndarray:
        x = math.cos(self.yaw) * math.cos(self.pitch)
        y = math.sin(self.pitch)
        z = math.sin(self.yaw) * math.cos(self.pitch)
        v = np.array([x, y, z], dtype=np.float64)
        n = np.linalg.norm(v)
        if n < 1e-9:
            return np.array([0.0, 0.0, -1.0], dtype=np.float64)
        return v / n

    def right(self) -> np.ndarray:
        world_up = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        r = np.cross(self.front(), world_up)
        n = np.linalg.norm(r)
        if n < 1e-9:
            return np.array([1.0, 0.0, 0.0], dtype=np.float64)
        return r / n

    def up(self) -> np.ndarray:
        r = self.right()
        f = self.front()
        u = np.cross(r, f)
        n = np.linalg.norm(u)
        if n < 1e-9:
            return np.array([0.0, 1.0, 0.0], dtype=np.float64)
        return u / n

    def apply_mouse_look(self, dx: float, dy: float) -> None:
        self.yaw += dx * config.CAMERA_MOUSE_SENSITIVITY
        self.pitch -= dy * config.CAMERA_MOUSE_SENSITIVITY
        self.pitch = max(-config.CAMERA_PITCH_CLAMP, min(config.CAMERA_PITCH_CLAMP, self.pitch))

    def apply_zoom_wheel(self, steps: int) -> None:
        if steps == 0:
            return
        self.fov_degrees -= steps * config.CAMERA_ZOOM_STEP
        self.fov_degrees = max(
            config.CAMERA_FOV_MIN,
            min(config.CAMERA_FOV_MAX, self.fov_degrees),
        )

    def move(self, forward: float, strafe: float, vertical: float, dt: float) -> None:
        """Gerak relatif ke arah pandangan (WASD) + vertikal world-space (Space/Ctrl)."""
        speed = config.CAMERA_MOVE_SPEED * dt
        f = self.front()
        r = self.right()
        world_up = np.array([0.0, 1.0, 0.0], dtype=np.float64)

        delta = forward * speed * f + strafe * speed * r + vertical * speed * world_up
        self.position = self.position + delta
