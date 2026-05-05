"""Pemetaan input Pygame ke aksi kamera."""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from src.camera.free_roam_camera import FreeRoamCamera


@dataclass
class InputState:
    forward: float = 0.0
    strafe: float = 0.0
    vertical: float = 0.0
    mouse_dx: float = 0.0
    mouse_dy: float = 0.0
    scroll_steps: int = 0

    def reset_per_frame_accumulators(self) -> None:
        self.mouse_dx = 0.0
        self.mouse_dy = 0.0
        self.scroll_steps = 0


@dataclass
class InputHandler:
    """Kumpulkan event keyboard dan mouse tiap frame.

    Roda mouse: scroll ke atas menambah `scroll_steps` positif dan memperkecil FOV di
    `FreeRoamCamera.apply_zoom_wheel` (zoom masuk).
    """

    mouse_grabbed: bool = True
    video_flags: int = 0
    _state: InputState = field(default_factory=InputState)

    def process_events(self) -> bool:
        """
        Proses antrian event. Return False jika aplikasi harus keluar.
        """
        self._state.reset_per_frame_accumulators()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.MOUSEWHEEL:
                self._state.scroll_steps += event.y
            if event.type == pygame.VIDEORESIZE and self.video_flags:
                w, h = event.w, event.h
                if w >= 320 and h >= 240:
                    pygame.display.set_mode((w, h), self.video_flags)

        keys = pygame.key.get_pressed()
        forward = 0.0
        if keys[pygame.K_w]:
            forward += 1.0
        if keys[pygame.K_s]:
            forward -= 1.0

        strafe = 0.0
        if keys[pygame.K_d]:
            strafe += 1.0
        if keys[pygame.K_a]:
            strafe -= 1.0

        vertical = 0.0
        if keys[pygame.K_SPACE]:
            vertical += 1.0
        if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
            vertical -= 1.0

        self._state.forward = forward
        self._state.strafe = strafe
        self._state.vertical = vertical

        if self.mouse_grabbed:
            dx, dy = pygame.mouse.get_rel()
            self._state.mouse_dx = float(dx)
            self._state.mouse_dy = float(dy)

        return True

    def apply_to_camera(self, camera: FreeRoamCamera, dt: float) -> None:
        camera.move(self._state.forward, self._state.strafe, self._state.vertical, dt)
        if self.mouse_grabbed:
            camera.apply_mouse_look(self._state.mouse_dx, self._state.mouse_dy)
        camera.apply_zoom_wheel(self._state.scroll_steps)
