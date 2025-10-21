# AppWatch

AppWatch adalah aplikasi GUI untuk memonitor dan mengelola paket yang terinstal di sistem Linux Anda.

## Fitur

- Menampilkan daftar semua paket terinstal
- Mendukung berbagai package manager (pacman, yay, flatpak, apt)
- Uninstall paket dengan mudah
- Tampilan modern dengan dukungan tema terang/gelap
- Mendukung berbagai desktop environment

## Persyaratan Sistem

- Python 3.6+
- PyQt5
- Desktop Environment (GNOME, KDE, XFCE, dll)
- Package manager yang didukung (minimal salah satu):
  - pacman (Arch Linux)
  - yay (AUR helper)
  - flatpak
  - apt (Debian/Ubuntu)

## Instalasi

1. Clone repository:

   ```bash
   git clone https://github.com/yooson-code/AppWatch.git
   cd AppWatch
   ```

2. Install PyQt5 sesuai distro Anda:

   **Arch Linux:**

   ```bash
   sudo pacman -S python-pyqt5
   ```

   **Ubuntu/Debian:**

   ```bash
   sudo apt install python3-pyqt5
   ```

   **Fedora:**

   ```bash
   sudo dnf install python3-qt5
   ```

3. Buat virtual environment (opsional):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   ```

4. Install dependensi Python:
   ```bash
   pip install PyQt5
   ```

## Menjalankan Aplikasi

```bash
python appwatch.py
```

## Troubleshooting

Jika window tidak muncul:

1. Pastikan Anda menjalankan dari desktop environment (bukan dari TTY)
2. Jika menggunakan SSH, gunakan flag -X:
   ```bash
   ssh -X username@host
   ```
3. Coba set DISPLAY manual:
   ```bash
   export DISPLAY=:0
   ```
4. Pastikan PyQt5 terinstal dengan benar sesuai distro Anda

## Kontribusi

Silakan buat pull request atau laporkan issues jika menemukan bug.

## Lisensi

MIT License
