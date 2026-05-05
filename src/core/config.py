"""Konfigurasi global aplikasi."""

# Jendela
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Simulasi Astronomi 3D — navigasi free-roam"

# Warna background (RGBA 0–1)
CLEAR_COLOR = (0.02, 0.02, 0.06, 1.0)

# Kamera gerak
CAMERA_MOVE_SPEED = 12.0
CAMERA_MOUSE_SENSITIVITY = 0.0025  # radian per piksel
CAMERA_PITCH_CLAMP = 1.553343  # ~89° — hindari singularitas

# Zoom (FOV derajat)
CAMERA_FOV_DEFAULT = 60.0
CAMERA_FOV_MIN = 30.0
CAMERA_FOV_MAX = 90.0
CAMERA_ZOOM_STEP = 2.5  # derajat per tick scroll

# Kliping proyeksi
PROJECTION_NEAR = 0.1
PROJECTION_FAR = 500.0

# Simulasi orbit (bukan skala nyata)
ORBIT_TIME_SCALE = 0.3

# Lintasan orbit (garis panduan visual di bidang XZ)
ORBIT_RING_SEGMENTS = 112
ORBIT_LINE_WIDTH = 1.25
ORBIT_LINE_RGB = (0.32, 0.40, 0.52)
ORBIT_RING_ALTITUDE = 0.0  # bidang sama dengan pusat Matahari untuk model tilt=0
