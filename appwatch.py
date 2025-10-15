import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPalette, QColor

# Import modules
from modules.pacman_tools import list_pacman_apps, uninstall_pacman
from modules.yay_tools import list_yay_apps, uninstall_yay
from modules.flatpak_tools import list_flatpak_apps, uninstall_flatpak
from modules.apt_tools import list_apt_apps, uninstall_apt
from modules.utils import detect_distro


class AppWatch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AppWatch - Linux Application Monitor")
        self.setGeometry(300, 150, 650, 550)

        self.is_dark = False  # default mode terang

        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # Judul
        self.label = QLabel("📦 AppWatch")
        self.label.setAlignment(Qt.AlignCenter)

        # Kolom pencarian
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Cari aplikasi...")
        self.search_box.textChanged.connect(self.filter_apps)

        # Tombol refresh
        self.refresh_btn = QPushButton(" Refresh")
        self.refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_btn.setIconSize(QSize(18, 18))
        self.refresh_btn.clicked.connect(self.load_apps)

        # Tombol light/dark mode
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setIcon(QIcon.fromTheme("weather-clear-night"))
        self.theme_btn.setIconSize(QSize(18, 18))
        self.theme_btn.clicked.connect(self.toggle_theme)

        top_layout.addWidget(self.search_box)
        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.theme_btn)

        # Tabel aplikasi
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Source", "Name", "Version"])
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 150)

        # Tombol uninstall
        self.uninstall_btn = QPushButton("❌ Uninstall Selected")
        self.uninstall_btn.clicked.connect(self.uninstall_app)

        main_layout.addWidget(self.label)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.uninstall_btn)
        self.setLayout(main_layout)

        self.all_apps = []
        self.load_apps()
        self.apply_light_theme()  # tema awal terang

    # ---------------------------
    #  Muat daftar aplikasi
    # ---------------------------
    def load_apps(self):
        self.table.setRowCount(0)
        distro = detect_distro()
        apps = []

        if "arch" in distro or "manjaro" in distro:
            apps = list_pacman_apps() + list_yay_apps() + list_flatpak_apps()
        elif "ubuntu" in distro or "debian" in distro or "mint" in distro:
            apps = list_apt_apps() + list_flatpak_apps()
        else:
            apps = list_flatpak_apps()

        self.all_apps = apps
        self.display_apps(apps)

    def display_apps(self, apps):
        self.table.setRowCount(0)
        for row, (src, name, version) in enumerate(apps):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(src))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(version))

    def filter_apps(self):
        query = self.search_box.text().lower()
        filtered = [app for app in self.all_apps if query in app[1].lower()]
        self.display_apps(filtered)

    def uninstall_app(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Pilih Aplikasi", "Silakan pilih aplikasi yang ingin dihapus.")
            return

        src = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()

        confirm = QMessageBox.question(self, "Konfirmasi",
                                       f"Yakin ingin menghapus {name} ({src})?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                if src == "pacman":
                    uninstall_pacman(name)
                elif src == "yay/AUR":
                    uninstall_yay(name)
                elif src == "flatpak":
                    uninstall_flatpak(name)
                elif src == "apt":
                    uninstall_apt(name)
                QMessageBox.information(self, "Sukses", f"{name} berhasil dihapus.")
                self.load_apps()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Gagal menghapus {name}.\n\n{str(e)}")

    # ---------------------------
    #  Fungsi tema (light/dark)
    # ---------------------------
    def toggle_theme(self):
        if self.is_dark:
            self.apply_light_theme()
            self.is_dark = False
            self.theme_btn.setText("🌙 Dark")
            self.theme_btn.setIcon(QIcon.fromTheme("weather-clear-night"))
        else:
            self.apply_dark_theme()
            self.is_dark = True
            self.theme_btn.setText("☀️ Light")
            self.theme_btn.setIcon(QIcon.fromTheme("weather-sunny"))

    def apply_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#fafafa"))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, QColor("#ffffff"))
        palette.setColor(QPalette.AlternateBase, QColor("#f0f0f0"))
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor("#e6e6e6"))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.Highlight, QColor("#0078D7"))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        QApplication.instance().setPalette(palette)
        QApplication.instance().setStyle("fusion")

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor("#2899F5"))
        QApplication.instance().setPalette(palette)
        QApplication.instance().setStyle("fusion")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWatch()
    window.show()
    sys.exit(app.exec_())
