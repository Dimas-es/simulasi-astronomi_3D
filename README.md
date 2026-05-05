# Simulasi Astronomi 3D (Python + Pygame + PyOpenGL)

Simulasi desktop sederhana: **Matahari + 8 planet** dengan orbit visual dan **garis lintasan orbit**, **kamera free-roam** (WASD + mouse look), **zoom** lewat scroll (mengubah FOV), serta HUD ringkas (kontrol + FPS).

> Skala jarak/kecepatan **bukan** model astronomi nyata—fokus pada visualisasi dan interaktivitas untuk tugas grafika komputer.

## Persyaratan

- Python **3.11 atau 3.12** sangat disarankan (biasanya ada **wheel** `pygame` siap pakai). Di **Python 3.14** sering belum ada wheel sehingga `pip` memaksa **kompilasi dari source** dan butuh header SDL/Freetype di sistem.
- GPU/driver OpenGL yang mendukung **fixed-function pipeline** (kompatibilitas OpenGL 1.x–2.1)
- Dependensi Python: lihat [`requirements.txt`](requirements.txt)

## Troubleshooting: `pip install pygame` gagal / `ModuleNotFoundError: pygame`

Log seperti `Downloading pygame-...tar.gz`, lalu `sdl2-config: command not found`, `freetype2` / `pkg-config` tidak ketemu, artinya **tidak ada wheel** untuk kombinasi OS + versi Python Anda, lalu build dari source **gagal** karena library pengembangan belum dipasang. Akibatnya `pygame` tidak terpasang dan `python main.py` gagal mengimpor `pygame`.

**Cara yang paling mudah**

1. Pasang Python **3.12** (misalnya lewat Fedora `python3.12`, pyenv, atau uv).
2. Buat venv baru dengan interpreter itu dan ulangi `pip install -r requirements.txt`.

**Jika Anda ingin tetap di Python Anda saat ini** — pasang paket sistem untuk bikin pygame dari source pada Fedora / RPM:

```bash
sudo dnf install SDL2-devel SDL2_mixer-devel SDL2_image-devel SDL2_ttf-devel \
  pkgconf-pkg-config freetype-devel cmake gcc python3-devel
```

Lalu ulangi `pip install -r requirements.txt`. Panduan upstream: https://www.pygame.org/wiki/Compilation

**Catatan:** baris `Defaulting to user installation because normal site-packages is not writable` artinya Anda menjalankan `pip` sebagai user biasa pada Python sistem tanpa venv aktif — gunakan **`python -m venv .venv`** seperti di bawah supaya lebih bersih dan mudah dibongkar pasang.

## Instalasi
```bash
cd /path/ke/uas_grafkom
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan

Dari root proyek (folder yang berisi `main.py`):

```bash
python main.py
```

Pastikan perintah dijalankan di lingkungan yang punya windowing (DISPLAY/X11/Wayland/WSLg).

## Kontrol

| Input | Fungsi |
|--------|--------|
| **W / S** | Maju / mundur |
| **A / D** | Geser kiri / kanan |
| **Spasi / Ctrl** | Naik / turun |
| **Mouse** | Putar pandangan (kursor ditangkap) |
| **Scroll** | Zoom: persempit / perlebar pandangan (FOV) |
| **Esc** | Keluar |

Ukuran jendela dapat diubah (mode **resize**).

## Struktur modul

- `main.py` — entry point.
- `src/core/config.py` — konstanta (kecepatan, FOV, jendela).
- `src/core/app.py` — game loop dan HUD overlay.
- `src/camera/free_roam_camera.py` — matematika kamera.
- `src/input/input_handler.py` — event keyboard, mouse relatif, wheel, resize.
- `src/simulation/solar_system.py` — data orbit planet.
- `src/rendering/` — setup OpenGL, pencahayaan, mesh bola (GLU), garis orbit, frame drawing.

## Batasan

- Tidak memakai shader modern (GLSL); menggunakan pipeline fixed-function seperti pada materi klasik OpenGL.
- Cahaya Matahari diabstraksikan menjadi **cahaya directional** agar stabil dengan transformasi kamera (tanpa komputasi posisi titik cahaya per frame).

## Lisensi / akademik

Proyek tugas mata kuliah — sesuaikan atribusi nama tim pada laporan bila diperlukan.
