#!/usr/bin/env python3
import sys
import os
import traceback
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QLineEdit, QCheckBox
)
from PyQt5.QtCore import Qt

from modules.pacman_tools import list_pacman_apps, uninstall_pacman
from modules.yay_tools import list_yay_apps, uninstall_yay
from modules.flatpak_tools import list_flatpak_apps, uninstall_flatpak
from modules.apt_tools import list_apt_apps, uninstall_apt
from modules.utils import detect_distro


class AppWatch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AppWatch — Linux Package Monitor')
        self.resize(900, 600)

        # setup logging
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

        self.dry_run = QCheckBox('Dry run (do not actually uninstall)')

        self.uninstall_btn = QPushButton('Uninstall Selected')
        self.uninstall_btn.setEnabled(False)
        self.uninstall_btn.clicked.connect(self.uninstall_selected)

        self.uninstall_checked_btn = QPushButton('Uninstall Checked')
        self.uninstall_checked_btn.setEnabled(False)
        self.uninstall_checked_btn.clicked.connect(self.uninstall_checked)

        top = QHBoxLayout()
        top.addWidget(self.search)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.dry_run)
        top.addWidget(self.uninstall_btn)
        top.addWidget(self.uninstall_checked_btn)

        # Table with checkbox column
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['', 'Source', 'Name', 'Version'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemSelectionChanged.connect(lambda: self.uninstall_btn.setEnabled(self.table.currentRow() >= 0))
        self.table.itemChanged.connect(self._on_item_changed)

        self.status = QLabel('')
        self.status.setObjectName('statusLabel')

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(self.table)
        layout.addWidget(self.status)
        self.setLayout(layout)

        self.all_apps = []
        # Load style and apps
        self.load_style()
        self.load_apps()

    def load_style(self):
        style_path = os.path.join(os.path.dirname(__file__), 'style.qss')
        try:
            with open(style_path, 'r') as f:
                style = f.read()
            QApplication.instance().setStyleSheet(style)
            self.logger.info('Loaded style from %s', style_path)
            self.status.setText('Style loaded')
        except Exception as e:
            self.logger.exception('Failed to load style')
            self.status.setText(f'Failed to load style: {e}')

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
            chk = QTableWidgetItem()
            chk.setFlags(chk.flags() | Qt.ItemIsUserCheckable)
            chk.setCheckState(Qt.Unchecked)
            self.table.setItem(r, 0, chk)
            self.table.setItem(r, 1, QTableWidgetItem(src))
            self.table.setItem(r, 2, QTableWidgetItem(name))
            self.table.setItem(r, 3, QTableWidgetItem(ver))

    def filter_apps(self):
        q = self.search.text().lower()
        filtered = [a for a in self.all_apps if q in a[1].lower()]
        self.table.setRowCount(0)
        for r, (src, name, ver) in enumerate(filtered):
            self.table.insertRow(r)
            chk = QTableWidgetItem()
            chk.setFlags(chk.flags() | Qt.ItemIsUserCheckable)
            chk.setCheckState(Qt.Unchecked)
            self.table.setItem(r, 0, chk)
            self.table.setItem(r, 1, QTableWidgetItem(src))
            self.table.setItem(r, 2, QTableWidgetItem(name))
            self.table.setItem(r, 3, QTableWidgetItem(ver))

    def _on_item_changed(self, item):
        try:
            if item.column() == 0:
                any_checked = any(self.table.item(r, 0).checkState() == Qt.Checked for r in range(self.table.rowCount()))
                self.uninstall_checked_btn.setEnabled(any_checked)
        except Exception:
            pass

    def uninstall_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        src = self.table.item(row, 1).text()
        name = self.table.item(row, 2).text()

        if QMessageBox.question(self, 'Confirm', f'Remove {name} from {src}?', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        try:
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
                self.logger.info('Dry run: would run: %s', cmd_display)
                QMessageBox.information(self, 'Dry run', f'Would run:\n{cmd_display}')
                self.status.setText(f'Dry run: {cmd_display}')
                return

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

    def uninstall_checked(self):
        checked = []
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item and item.checkState() == Qt.Checked:
                src = self.table.item(r, 1).text()
                name = self.table.item(r, 2).text()
                checked.append((r, src, name))

        if not checked:
            return

        names = ', '.join([n for (_, _, n) in checked])
        if QMessageBox.question(self, 'Confirm', f'Remove {len(checked)} packages?\\n{names}', QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        results = []
        for r, src, name in checked:
            try:
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
                    self.logger.info('Dry run: would run: %s', cmd_display)
                    results.append((name, True, 'dry-run'))
                    continue

                self.logger.info('Running uninstall: %s', cmd_display)
                action()
                results.append((name, True, 'ok'))
            except subprocess.CalledProcessError as cpe:
                err = cpe.stderr or cpe.output or str(cpe)
                results.append((name, False, err))
                self.logger.error('Uninstall failed for %s: %s', name, err)
            except Exception as e:
                results.append((name, False, str(e)))
                self.logger.exception('Error uninstalling %s', name)

        ok = [n for n, s, _ in results if s]
        fail = [(n, t) for n, s, t in results if not s]
        msg = f'Removed: {len(ok)}\\nFailed: {len(fail)}'
        if fail:
            msg += '\\n' + '\\n'.join([f'{n}: {err}' for n, err in fail])
        QMessageBox.information(self, 'Uninstall summary', msg)
        self.load_apps()


def main():
    display = os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')
    if not display:
        print('Warning: DISPLAY/WAYLAND_DISPLAY not set; ensure you run from a desktop session')

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
