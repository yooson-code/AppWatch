import subprocess

def list_flatpak_apps():
    try:
        result = subprocess.run(["flatpak", "list", "--columns=application,version"], stdout=subprocess.PIPE, text=True)
        apps = []
        for line in result.stdout.splitlines()[1:]:
            parts = line.split("\t")
            if len(parts) >= 2:
                name, version = parts[0], parts[1]
                apps.append(("flatpak", name, version))
        return apps
    except FileNotFoundError:
        return []

def uninstall_flatpak(name):
    subprocess.run(["flatpak", "uninstall", "-y", name])
