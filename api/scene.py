"""Unpack the gzipped 3D scene buffer.

data.bin is 26MB raw and 2.7MB gzipped, so only the .gz is committed and only
the .gz is bundled into installers. It is expanded once at startup. Without it
the GLTF loader 404s and the viewport silently falls back to the flat 2D map.
"""
import gzip
import shutil
import sys
from pathlib import Path


def scene_dir() -> Path:
    """Where assets/scene lives — inside the PyInstaller bundle when frozen."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets" / "scene"
    return Path(__file__).parent.parent / "assets" / "scene"


def ensure_scene(target_dir: Path | None = None) -> bool:
    """Expand data.bin.gz if missing or stale. Returns True if data.bin is ready.

    Never raises: a failure here should degrade to the 2D map, not stop the app.
    """
    src_dir = scene_dir()
    gz = src_dir / "data.bin.gz"
    out = (target_dir or src_dir) / "data.bin"

    if not gz.exists():
        return out.exists()
    # Re-unpack when the archive is newer, e.g. after a pull updates the scene.
    if out.exists() and out.stat().st_mtime >= gz.stat().st_mtime:
        return True

    print("Unpacking 3D scene geometry...")
    # Write to a temp file first so an interrupted run can't leave a truncated
    # data.bin behind — corrupt geometry fails far messier than a missing file.
    tmp = out.with_suffix(".bin.part")
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(gz, "rb") as fsrc, open(tmp, "wb") as fdst:
            shutil.copyfileobj(fsrc, fdst)
        tmp.replace(out)
        return True
    except Exception as exc:
        tmp.unlink(missing_ok=True)
        print(f"Failed to unpack scene geometry: {exc}")
        print("The viewport will fall back to the 2D map.")
        return False
