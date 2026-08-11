# PyInstaller spec for the rune-claude backend.
# Produces a standalone binary so end users need no Python install.
# Built via `npm run build:backend` (scripts/build-backend.js).
import os
from pathlib import Path

ROOT = Path(os.environ.get("RUNE_ROOT", os.getcwd())).resolve()


def tree(src: str, exclude=()):
    """Collect a directory as (source, dest) datas, skipping excluded names."""
    out = []
    base = ROOT / src
    if not base.exists():
        return out
    for path in base.rglob("*"):
        if not path.is_file():
            continue
        if any(part in exclude for part in path.parts):
            continue
        if path.name in exclude:
            continue
        out.append((str(path), str(path.parent.relative_to(ROOT))))
    return out


# assets/scene/data.bin is the 26MB expanded buffer — ship only data.bin.gz and
# let api.scene.ensure_scene() expand it at first run. Saves ~24MB per installer.
datas = (
    tree("assets", exclude={"data.bin", "data.bin.part"})
    + tree("renderer")
    + tree("tui/data")
)

a = Analysis(
    [str(ROOT / "server_main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # flask-sock's websocket backend is imported lazily by name.
        "simple_websocket",
        "engineio.async_drivers.threading",
    ],
    hookspath=[],
    runtime_hooks=[],
    # Trim the GUI/test stacks PyInstaller otherwise drags in.
    excludes=["tkinter", "textual", "pytest", "PIL.ImageQt", "matplotlib", "numpy"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="rune-claude-server",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # console=True keeps stderr attached so backend crashes are visible in logs.
    # A windowed build swallows per-request logging and makes debugging guesswork.
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
