# Simulasi astronomi 3D dengan navigasi free-roam camera berbasis OpenGL

**Mata kuliah:** Grafika Komputer  

**Program Studi Informatika**  
**Fakultas Teknik**  
**Universitas Siliwangi**  
**Tahun 2026**

---

**Disusun oleh:**

| Nama | NIM |
|------|-----|
| Rafli Putra Nur Syabani | 237006083 |
| Ginanjar Aditiy Prianata | 237006084 |
| Muhamad Rizki | 237006085 |
| Dimas Setiawan | 237006090 |
| Muhammad Rai Akmal | 237006092 |

---

Aplikasi desktop **Python + Pygame + PyOpenGL**: **Matahari**, **planet dengan tekstur file atau pola procedural**, **nama 3D di atas tiap benda**, **Bulan** mengorbit Bumi, **sabuk asteroid**, **meteor**, **objek metalik pengunjung**, garis lintasan orbit, serta **kamera free-roam** dan **zoom FOV** lewat scroll roda mouse.

> Skala jarak dan kecepatan **bukan** model astronomi sebenarnya; tujuan utamanya visualisasi dan interaksi untuk pembelajaran grafika komputer.

## Yang perlu disiapkan (ringkas)

| Item | Keterangan |
|------|------------|
| **Python** | **3.11 atau 3.12** paling mudah (`pygame` biasanya dapat **wheel**, tanpa kompilasi). Hindari Python terlalu baru (mis. 3.14) jika `pip install` sering gagal — lihat [Jika instalasi gagal](#jika-instalasi-gagal). |
| **Folder proyek** | Anda harus berada di **root repo**: di dalamnya ada berkas **`main.py`** dan folder **`src/`**. |
| **Layar grafis** | Aplikasi membuka **jendela**; jalankan dari desktop (Linux/macOS/Windows). Di **WSL** butuh **WSLg** atau X server; jalankan dari **PowerShell Prompt WSL**, bukan SSH tanpa display. |
| **GPU/driver** | OpenGL **fixed-function** (umum pada driver Intel/AMD/NVIDIA untuk tugas klasik GL 1.x–2.1). |

Dependensi Python tercantum di [`requirements.txt`](requirements.txt) (`pygame`, `PyOpenGL`, `numpy`, `pillow`).

## Instalasi (langkah demi langkah)

Ikuti urutan ini; **jangan lewati aktivasi venv** sebelum `pip install` dan `python main.py`.

### 1. Buka terminal di folder proyek

Contoh setelah meng-clone atau mengekstrak zip:

```bash
cd /path/ke/uas_grafkom
```

Pastikan `ls` (Linux/macOS) atau `dir` (Windows) menampilkan **`main.py`**.

### 2. Periksa versi Python (disarankan 3.11 atau 3.12)

```bash
python --version
```

Jika perintah `python` tidak ada, coba `python3 --version` (Linux/macOS) atau `py -3.12 --version` (Windows, jika Python dari python.org).

### 3. Buat lingkungan virtual (venv)

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (Command Prompt atau PowerShell):**

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Setelah aktif, biasanya prompt menampilkan `(.venv)`. **Semua langkah berikutnya** (`pip`, `python main.py`) jalankan **di terminal yang sama** selagi venv masih aktif.

### 4. Perbarui pip (opsional, mengurangi masalah unduhan)

```bash
python -m pip install --upgrade pip
```

### 5. Pasang dependensi proyek

```bash
pip install -r requirements.txt
```

Tunggu sampai selesai tanpa error merah di akhir.

### 6. Uji cepat: modul terpasang

```bash
python -c "import pygame; import OpenGL.GL; print('Dependensi utama OK')"
```

Jika keluar **`Dependensi utama OK`**, langkah instalasi untuk Python sudah beres.

### 7. Jalankan program

Masih di **folder yang sama** dengan `main.py`, dengan venv **aktif**:

```bash
python main.py
```

Seharusnya muncul jendela simulasi. Tekan **Esc** untuk keluar.

---

**Catatan Windows:** kalau `python` tidak dikenali setelah aktivasi venv, gunakan **`py`** hanya untuk membuat venv (`py -3.12 -m venv .venv`); di dalam venv aktiv, biasanya **`python`** sudah menunjuk ke interpreter yang benar.

**Catatan WSL/Linux headless:** error seperti `unable to open display` berarti tidak ada sesi grafis — jalankan dari sesi desktop yang punyi `DISPLAY`, atau pakai **WSLg** di Windows 11.

## Jika instalasi gagal

Gejala umum:

- **`Downloading pygame-...tar.gz`** lalu error kompilasi, **`sdl2-config: command not found`**, **`freetype`** / **`pkg-config`** — artinya tidak ada wheel untuk kombinasi **OS + versi Python** Anda dan build dari source gagal.

**Solusi paling cepat**

1. Pasang Python **3.12** dari [python.org](https://www.python.org/downloads/) atau manajer paket distro (`python3.12`, pyenv, uv).
2. Hapus venv lama: `rm -rf .venv` (Linux/macOS) atau hapus folder `.venv` di Explorer (Windows).
3. Buat venv lagi **dengan interpreter 3.12** (ulangi [langkah 3](#3-buat-lingkungan-virtual-venv)) lalu **`pip install -r requirements.txt`**.

**Jika ingin tetap memakai versi Python saat ini** — pasang *header/library* pengembangan SDL untuk build pygame dari source:

- **Fedora / RPM:**

  ```bash
  sudo dnf install SDL2-devel SDL2_mixer-devel SDL2_image-devel SDL2_ttf-devel \
    pkgconf-pkg-config freetype-devel cmake gcc python3-devel
  ```

- **Ubuntu / Debian:**

  ```bash
  sudo apt update
  sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libfreetype-dev pkg-config build-essential python3-dev
  ```

Lalu ulangi `pip install -r requirements.txt`. Panduan lanjutan: https://www.pygame.org/wiki/Compilation

**`Defaulting to user installation because normal site-packages is not writable`**

Anda menjalankan `pip` **tanpa venv** atau tanpa hak yang tepat. Selalu gunakan **`python -m venv .venv`** dan **`activate`** seperti di atas agar paket terpasang ke folder proyek.

**`ModuleNotFoundError` saat `python main.py`**

Biasanya venv **tidak aktif** atau Anda menjalankan `python` dari luar folder proyek. Pastikan: (1) prompt ada `(.venv)`, (2) `main.py` ada di direktori kerja saat ini, (3) perintahnya `python main.py` (bukan skrip lain).

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

## Aset tekstur (opsional)

Letakkan gambar di folder `assets/textures/` (relatif ke root proyek). Jika berkas tidak ada, program memakai **tekstur procedural** otomatis berdasarkan warna dasar planet.

Nama berkas yang dikenali (ekstensi `.jpg` atau `.png`; contoh memakai JPG):

| Kunci | Nama berkas disarankan |
|--------|-------------------------|
| Matahari | `sun.jpg` |
| Merkurius … Neptunus | `mercury.jpg` … `neptune.jpg` (lihat konstanta pada `src/rendering/textures.py`) |
| Bulan | `moon.jpg` |

## Performa (`src/core/config.py`)

- `USE_PLANET_TEXTURES` — matikan untuk mesin lemah (kembali warna solid pada bola).
- `USE_LABELS` — matikan nama 3D billboard.
- `ASTEROID_COUNT`, `METEOR_COUNT` — kurangi jumlah partikel jika FPS turun.

## Struktur modul

- `main.py` — titik masuk aplikasi.
- `src/core/config.py` — konstanta (kecepatan, FOV, jumlah asteroid/meteor, toggle tekstur & label).
- `src/core/app.py` — game loop, update simulasi, HUD overlay.
- `src/camera/free_roam_camera.py` — matematika kamera free-roam.
- `src/input/input_handler.py` — event keyboard, mouse relatif, wheel, resize.
- `src/simulation/solar_system.py` — Matahari, planet, Bulan.
- `src/simulation/asteroid_belt.py` — sabuk asteroid.
- `src/simulation/meteors.py` — meteor.
- `src/simulation/exotic_visitors.py` — objek asing berkilau.
- `src/rendering/` — `renderer.py`, `textures.py`, `labels.py`, `asteroid_mesh.py`, `primitives.py`, `lighting.py`.

## Batasan

- Tidak memakai shader modern (GLSL); menggunakan pipeline fixed-function seperti pada materi klasik OpenGL.
- Cahaya Matahari diabstraksikan menjadi **cahaya directional** agar stabil dengan transformasi kamera (tanpa komputasi posisi titik cahaya per frame).

## Lisensi dan penggunaan akademik

Proyek ini dibuat untuk keperluan **tugas/kuliah Grafika Komputer** Universitas Siliwangi. Penggunaan kembali mengikuti ketentuan dosen/pemrogram masing-masing.
