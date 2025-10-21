import subprocess
from .utils import run_privileged


def list_apt_apps():
    try:
        result = subprocess.run(["apt", "list", "--installed"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        apps = []
        for line in result.stdout.splitlines():
            if "/" in line and "[" not in line:
                try:
                    name = line.split("/")[0]
                    version = line.split()[1]
                    apps.append(("apt", name, version))
                except IndexError:
                    continue
        return apps
    except FileNotFoundError:
        return []


def uninstall_apt(name):
    return run_privileged(["apt", "remove", "-y", name])
