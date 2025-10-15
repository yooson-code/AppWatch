import platform

def detect_distro():
    try:
        info = platform.freedesktop_os_release()
        return info.get("ID", "").lower()
    except Exception:
        return "unknown"
