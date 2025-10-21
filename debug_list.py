#!/usr/bin/env python3
import os
import shutil
import sys
from modules.utils import detect_distro
from modules import pacman_tools, yay_tools, flatpak_tools, apt_tools

print('ENV DISPLAY=', os.environ.get('DISPLAY'))
print('ENV WAYLAND_DISPLAY=', os.environ.get('WAYLAND_DISPLAY'))
print('ENV XDG_SESSION_TYPE=', os.environ.get('XDG_SESSION_TYPE'))

distro = detect_distro()
print('Detected distro:', distro)
print('Binaries present:')
print('  pacman ->', shutil.which('pacman'))
print('  yay    ->', shutil.which('yay'))
print('  flatpak->', shutil.which('flatpak'))
print('  apt    ->', shutil.which('apt'))

apps = []
try:
    if 'arch' in distro or 'manjaro' in distro:
        apps = pacman_tools.list_pacman_apps() + yay_tools.list_yay_apps() + flatpak_tools.list_flatpak_apps()
    elif 'ubuntu' in distro or 'debian' in distro or 'mint' in distro:
        apps = apt_tools.list_apt_apps() + flatpak_tools.list_flatpak_apps()
    else:
        apps = flatpak_tools.list_flatpak_apps()
except Exception as e:
    print('Error listing apps:', e)
    sys.exit(2)

print('Detected apps count:', len(apps))
for src, name, ver in apps[:200]:
    print(f"{src}\t{name}\t{ver}")
