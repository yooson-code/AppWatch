import subprocess

def list_pacman_apps():
    try:
        result = subprocess.run(["pacman", "-Q"], stdout=subprocess.PIPE, text=True)
        apps = []
        for line in result.stdout.splitlines():
            if line.strip():
                try:
                    name, version = line.split()
                    apps.append(("pacman", name, version))
                except ValueError:
                    continue
        return apps
    except FileNotFoundError:
        return []

def uninstall_pacman(name):
    subprocess.run(["sudo", "pacman", "-Rns", "--noconfirm", name])
