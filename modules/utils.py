import platform
import shutil
import subprocess
import os

def detect_distro():
    try:
        info = platform.freedesktop_os_release()
        return info.get("ID", "").lower()
    except Exception:
        # Fallback: try reading /etc/os-release
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=", 1)[1].strip().strip('"').lower()
        except Exception:
            return "unknown"


def run_privileged(cmd_list):
    """Run a command with elevated privileges when needed.

    Prefers running as-is when already root, then falls back to pkexec, then sudo.
    Raises subprocess.CalledProcessError on non-zero exit so callers can handle errors.
    Returns subprocess.CompletedProcess on success.
    """
    if os.geteuid() == 0:
        prefix = []
    elif shutil.which("pkexec"):
        prefix = ["pkexec"]
    elif shutil.which("sudo"):
        prefix = ["sudo"]
    else:
        raise RuntimeError("Tidak dapat menemukan mekanisme elevasi (pkexec/sudo) dan aplikasi tidak dijalankan sebagai root.")

    full_cmd = prefix + list(cmd_list)
    result = subprocess.run(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        # Raise to allow caller to show stderr
        raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)
    return result
