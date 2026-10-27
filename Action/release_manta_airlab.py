from __future__ import annotations

import subprocess
import sys
from pathlib import Path


# Toggle these flags before running the script.
BUILD_INSTALLER = True
UPLOAD_TO_SITE = True
AUTO_BUMP_PATCH = True
SIGN_RELEASE = True

# Publish targets used by the release launcher.
SITE_REPO_ROOT = r"C:\Users\fabio\OneDrive\DUILIO.CC"
REMOTE_SUBDIR = "manta-airfoil-tools/downloads"
REMOTE_BASE_URL = "https://duilio.cc/manta-airfoil-tools/downloads"


def run_step(cmd: list[str], title: str) -> None:
    print(f"[manta-release] {title}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def _probe_python(candidate: str) -> str | None:
    try:
        result = subprocess.run(
            [candidate, "-c", "import sys; print(sys.executable); raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    resolved = (result.stdout or "").strip().splitlines()
    return resolved[-1].strip() if resolved else candidate


def resolve_python_for_build() -> str:
    if sys.version_info >= (3, 11):
        return sys.executable or "python"

    candidates = [
        str(Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python311" / "python.exe"),
        str(Path.home() / "AppData" / "Local" / "Programs" / "Python" / "Python312" / "python.exe"),
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            probed = _probe_python(candidate)
            if probed:
                print(f"[manta-release] using build python: {probed}")
                return probed

    try:
        result = subprocess.run(
            ["py", "-3.11", "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            candidate = (result.stdout or "").strip().splitlines()
            if candidate:
                probed = _probe_python(candidate[-1].strip())
                if probed:
                    print(f"[manta-release] using build python: {probed}")
                    return probed
    except OSError:
        pass

    raise SystemExit(
        "Python 3.11+ not found automatically. Install Python 3.11 or run with "
        "'py -3.11 .\\Action\\release_manta_airlab.py'."
    )


def read_version(repo_root: Path) -> str:
    version_path = repo_root / "VERSION"
    raw = version_path.read_text(encoding="utf-8").strip()
    if not raw:
        raise SystemExit("VERSION file is empty")
    return raw


def bump_patch_version(version: str) -> str:
    parts = version.strip().split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise SystemExit(f"Unsupported VERSION format: {version!r}. Expected MAJOR.MINOR.PATCH")
    major, minor, patch = (int(part) for part in parts)
    return f"{major}.{minor}.{patch + 1}"


def write_version(repo_root: Path, version: str) -> None:
    (repo_root / "VERSION").write_text(version + "\n", encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    version = read_version(repo_root)
    if BUILD_INSTALLER and AUTO_BUMP_PATCH:
        version = bump_patch_version(version)
        write_version(repo_root, version)
        print(f"[manta-release] bumped VERSION to {version}")

    builder_script = repo_root / "release_tooling_nuitka" / "scripts" / "build_exe_manta_airlab_nuitka.ps1"
    sign_script = repo_root / "release_tooling_nuitka" / "scripts" / "sign_manta_release.ps1"
    publish_script = repo_root / "release_tooling_nuitka" / "scripts" / "publish_installer_to_duilio_cc.ps1"
    python_exe = resolve_python_for_build()

    if BUILD_INSTALLER:
        run_step(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(builder_script),
                "-PythonExe",
                python_exe,
                "-AppVersion",
                version,
            ],
            f"build installer via Nuitka ({version})",
        )
    else:
        print("[manta-release] build skipped (BUILD_INSTALLER = False)")

    if SIGN_RELEASE:
        run_step(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(sign_script)],
            "sign release artifacts",
        )
    else:
        print("[manta-release] signing skipped (SIGN_RELEASE = False)")

    if UPLOAD_TO_SITE:
        run_step(
            [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(publish_script),
                "-SiteRepoRoot",
                SITE_REPO_ROOT,
                "-RemoteSubdir",
                REMOTE_SUBDIR,
                "-RemoteBaseUrl",
                REMOTE_BASE_URL,
            ],
            "publish installer to duilio.cc",
        )
    else:
        print("[manta-release] upload skipped (UPLOAD_TO_SITE = False)")

    print("[manta-release] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
