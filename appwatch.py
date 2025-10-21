#!/usr/bin/env python3
import sys
import os
import traceback

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor

from modules.pacman_tools import list_pacman_apps, uninstall_pacman
from modules.yay_tools import list_yay_apps, uninstall_yay
from modules.flatpak_tools import list_flatpak_apps, uninstall_flatpak
from modules.apt_tools import list_apt_apps, uninstall_apt
from modules.utils import detect_distro
from modules.pacman_tools import list_pacman_apps
from modules.yay_tools import list_yay_apps
from modules.flatpak_tools import list_flatpak_apps
from modules.apt_tools import list_apt_apps

import subprocess


class AppWatch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AppWatch — Linux Package Monitor')
        self.resize(900, 600)

        # Setup logging
        import logging
        log_path = os.path.join(os.path.dirname(__file__), 'appwatch.log')
        logging.basicConfig(filename=log_path, level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s')
        self.logger = logging.getLogger('appwatch')
        self.logger.info('AppWatch starting')

        # Controls
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search...')
        self.search.textChanged.connect(self.filter_apps)

        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.clicked.connect(self.load_apps)

        # Dry-run checkbox (don't actually execute uninstall when checked)
        self.dry_run = QCheckBox('Dry run (do not actually uninstall)')

        self.uninstall_btn = QPushButton('Uninstall Selected')
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.clicked.connect(self.uninstall_selected)

        top = QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.dry_run)
        top.addWidget(self.uninstall_btn)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Source', 'Name', 'Version'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(lambda: self.uninstall_btn.setEnabled(self.table.currentRow() >= 0))

        self.status = QLabel('')

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.table)
        layout.addWidget(self.status)
        self.setLayout(layout)

        self.all_apps = []
        self.load_apps()

    def load_apps(self):
        self.table.setRowCount(0)
        distro = detect_distro()
        apps = []
        try:
            if 'arch' in distro or 'manjaro' in distro:
                apps = list_pacman_apps() + list_yay_apps() + list_flatpak_apps()
            elif 'ubuntu' in distro or 'debian' in distro or 'mint' in distro:
                apps = list_apt_apps() + list_flatpak_apps()
            else:
                apps = list_flatpak_apps()
        except Exception as e:
            self.status.setText(f'Error loading apps: {e}')
            traceback.print_exc()
            self.logger.exception('Error loading apps')

        self.all_apps = apps
        for r, (src, name, ver) in enumerate(apps):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(src))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(ver))

    def filter_apps(self):
        q = self.search.text().lower()
        filtered = [a for a in self.all_apps if q in a[1].lower()]
        self.table.setRowCount(0)
        for r, (src, name, ver) in enumerate(filtered):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(src))
            self.table.setItem(r, 1, QTableWidgetItem(name))
            self.table.setItem(r, 2, QTableWidgetItem(ver))

    def uninstall_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        src = self.table.item(row, 0).text()
        name = self.table.item(row, 1).text()

        if QMessageBox.question(self, 'Confirm', f'Remove {name} from {src}?', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        try:
            # Map source to command (for dry-run display) and to call
            cmd = None
            if src == 'pacman':
                cmd = ['pacman', '-Rns', '--noconfirm', name]
                action = lambda: uninstall_pacman(name)
            elif src == 'yay/AUR':
                cmd = ['yay', '-Rns', '--noconfirm', name]
                action = lambda: uninstall_yay(name)
            elif src == 'flatpak':
                cmd = ['flatpak', 'uninstall', '-y', name]
                action = lambda: uninstall_flatpak(name)
            elif src == 'apt':
                cmd = ['apt', 'remove', '-y', name]
                action = lambda: uninstall_apt(name)
            else:
                raise RuntimeError('Unsupported source')

            cmd_display = ' '.join(cmd) if cmd else name
            if self.dry_run.isChecked():
                # Do not execute; just log and show info
                self.logger.info('Dry run: would run: %s', cmd_display)
                QMessageBox.information(self, 'Dry run', f'Would run:\n{cmd_display}')
                self.status.setText(f'Dry run: {cmd_display}')
                return

            # Execute the uninstall action and log
            self.logger.info('Running uninstall: %s', cmd_display)
            action()
            self.logger.info('Uninstall requested for %s (%s)', name, src)
            self.status.setText(f'{name} removed (attempted)')
            self.load_apps()
        except subprocess.CalledProcessError as cpe:
            err = cpe.stderr or cpe.output or str(cpe)
            self.status.setText(f'Uninstall failed: {err}')
            QMessageBox.critical(self, 'Uninstall failed', err)
            self.logger.error('Uninstall failed for %s: %s', name, err)
        except Exception as e:
            self.status.setText(f'Error: {e}')
            traceback.print_exc()
            self.logger.exception('Error during uninstall')


def main():
    # Quick display check
    display = os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
    if not display:
        print('Warning: DISPLAY/WAYLAND_DISPLAY not set; ensure you run from a desktop session')

    # Headless/list modes: print detected packages and exit
    args = sys.argv[1:]
    if '--list' in args or '--headless' in args:
        distro = detect_distro()
        apps = []
        try:
            if 'arch' in distro or 'manjaro' in distro:
                apps = list_pacman_apps() + list_yay_apps() + list_flatpak_apps()
            elif 'ubuntu' in distro or 'debian' in distro or 'mint' in distro:
                apps = list_apt_apps() + list_flatpak_apps()
            else:
                apps = list_flatpak_apps()
        except Exception as e:
            print('Error listing apps:', e)
            return 2

        for src, name, ver in apps:
            print(f'{src}\t{name}\t{ver}')
        return 0

    app = QApplication(sys.argv)
    win = AppWatch()
    win.show()
    return app.exec_()


if __name__ == '__main__':
    rc = main()
    sys.exit(rc)
