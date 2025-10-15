import subprocess

def list_yay_apps():
    try:
        result = subprocess.run(["yay", "-Qm"], stdout=subprocess.PIPE, text=True)
        apps = []
        for line in result.stdout.splitlines():
            if line.strip():
                try:
                    name, version = line.split()
                    apps.append(("yay/AUR", name, version))
                except ValueError:
                    continue
        return apps
    except FileNotFoundError:
        return []

def uninstall_yay(name):
    subprocess.run(["yay", "-Rns", "--noconfirm", name])
