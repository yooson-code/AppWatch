# 🧩 AppWatch – Linux Application Monitor

AppWatch adalah aplikasi GUI lintas distro untuk memantau dan mengelola aplikasi yang terinstal di Linux.  
Didesain dengan tampilan modern dan ringan menggunakan **Python + PyQt5**, AppWatch mampu mengenali paket dari **pacman, yay (AUR), apt**, dan **flatpak** secara otomatis tergantung distro yang digunakan.

---

## ✨ Fitur Utama

✅ Menampilkan semua aplikasi dari berbagai sumber:

- 🧱 **pacman** (Arch, Manjaro)
- 🧩 **yay (AUR)**
- 📦 **apt** (Ubuntu, Debian, Mint)
- 🪶 **flatpak**

✅ Fitur lainnya:

- ❌ Uninstall langsung dari GUI
- 🧠 Deteksi otomatis distro (Arch, Ubuntu, Debian, dsb.)
- 🪟 Ringan & kompatibel dengan KDE/Qt environment

---

## 🧱 Persyaratan

Pastikan sistem kamu sudah memiliki dependensi berikut:

```bash
# Untuk Arch / Manjaro
sudo pacman -S python python-pyqt5 flatpak polkit
yay -S yay

# Untuk Ubuntu / Debian / Mint
sudo apt install python3 python3-pyqt5 flatpak policykit-1 -y

## 📜 Cara Menjalankannya

git clone https://github.com/yooson-code/AppWatch
cd appwatch
sudo python3 appwatch.py
```
