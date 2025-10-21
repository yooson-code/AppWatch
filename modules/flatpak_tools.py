import subprocess
from .utils import run_privileged


def list_flatpak_apps():
	try:
		result = subprocess.run(["flatpak", "list", "--columns=application,version"], stdout=subprocess.PIPE, text=True)
		apps = []
		# flatpak list prints a header on some systems, try to skip it if present
		lines = result.stdout.splitlines()
		# if header-like first line contains 'Application' or 'application', skip it
		start = 0
		if lines and ("Application" in lines[0] or "application" in lines[0]):
			start = 1
		for line in lines[start:]:
			parts = line.split("\t")
			if len(parts) >= 2:
				name, version = parts[0].strip(), parts[1].strip()
				apps.append(("flatpak", name, version))
		return apps
	except FileNotFoundError:
		return []


def uninstall_flatpak(name):
	return run_privileged(["flatpak", "uninstall", "-y", name])
