"""Konfigurasi global aplikasi."""

# Jendela — fallback saat tidak bisa membaca ukuran desktop atau WINDOW_MATCH_DESKTOP=False
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_TITLE = "Simulasi Astronomi 3D — navigasi free-roam"
# True: pakai pygame.display.Info() current_w/h monitor utama saat startup
WINDOW_MATCH_DESKTOP = True
# Batas ukuran pertama jika WINDOW_MATCH_DESKTOP (skala seragam, pertahankan rasio).
# Proses "killed" tanpa traceback di Linux sering dari OOM; layar native 4K+ memperbesar framebuffer GL.
# (0, 0) = tanpa batas.
WINDOW_INIT_MAX_WIDTH = 1920
WINDOW_INIT_MAX_HEIGHT = 1080

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

# Aset tekstur (subfolder relatif ke root proyek)
ASSETS_TEXTURES_SUBDIR = "assets/textures"

# Tekstur / label (matikan di mesin lemah)
USE_PLANET_TEXTURES = True
USE_LABELS = True
TEXTURE_MAX_EDGE = 512  # boleh dinaikkan jika VGA kuat untuk tekstur file/procedural lebih tajam

# Matahari — lapisan halo (skala pengali SUN_RADIUS dunia, kemudian alpha + warna additive)
SUN_HALO_LAYER_SCALES = (1.1, 1.24)
SUN_HALO_LAYER_ALPHAS = (0.28, 0.14)
SUN_HALO_LAYER_RGB = ((1.0, 0.78, 0.38), (1.0, 0.48, 0.12))

# Saturnus — cincin planar (radii pengali dari body_radius planet tersebut)
SATURN_RING_SEGMENT_COUNT = 112
SATURN_RING_POLYGON_OFFSET = (-1.2, -3.5)
SATURN_RING_BANDS = (
    # (rel_inner, rel_outer, rgba 0–1)
    (1.28, 1.92, (0.93, 0.86, 0.68, 0.52)),
    (1.98, 2.38, (0.84, 0.76, 0.58, 0.38)),
    (2.48, 2.85, (0.68, 0.58, 0.44, 0.26)),
)

# Sabuk asteroid
ASTEROID_COUNT = 140
ASTEROID_BELT_R_MIN = 11.5
ASTEROID_BELT_R_MAX = 13.2
ASTEROID_SIZE_MIN = 0.04
ASTEROID_SIZE_MAX = 0.14
ASTEROID_ORBIT_SPEED_MIN = 0.05
ASTEROID_ORBIT_SPEED_MAX = 0.11
ASTEROID_ROT_SPEED_MAX = 1.2

# Meteor
METEOR_COUNT = 18
METEOR_SPEED_MIN = 24.0
METEOR_SPEED_MAX = 55.0
METEOR_WORLD_BOUND = 85.0
METEOR_RADIUS = 0.06

# Benda asing (flyby elips)
EXOTIC_VISITOR_COUNT = 2
EXOTIC_FLYBY_RADIUS = 42.0
EXOTIC_FLYBY_ANGULAR_SPEED = 0.04
EXOTIC_SCALE = 1.4

# Nama di atas planet (billboard)
LABEL_OFFSET_FACTOR = 1.42
LABEL_FONT_PT = 17
# Skala world: perkiraan lebar ~ lebar_tekstur_px * faktor (lebih kecil = label lebih kecil)
LABEL_WORLD_PER_TEX_PX = 0.0055
LABEL_TEXT_FG = (255, 251, 245)
LABEL_TEXT_OUTLINE = (10, 12, 28)
