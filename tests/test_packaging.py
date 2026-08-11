"""Checks for the packaging path: scene unpacking and platform guards."""
import gzip
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.scene import ensure_scene


def test_ensure_scene_unpacks(tmp_path):
    """A .gz in the scene dir expands to data.bin with identical bytes."""
    payload = b"lumbridge" * 5000
    (tmp_path / "data.bin.gz").write_bytes(gzip.compress(payload))

    import api.scene
    original = api.scene.scene_dir
    api.scene.scene_dir = lambda: tmp_path
    try:
        assert ensure_scene() is True
        assert (tmp_path / "data.bin").read_bytes() == payload
    finally:
        api.scene.scene_dir = original


def test_ensure_scene_survives_corrupt_archive(tmp_path):
    """A truncated .gz must not leave a partial data.bin behind."""
    (tmp_path / "data.bin.gz").write_bytes(gzip.compress(b"x" * 1000)[:20])

    import api.scene
    original = api.scene.scene_dir
    api.scene.scene_dir = lambda: tmp_path
    try:
        assert ensure_scene() is False
        assert not (tmp_path / "data.bin").exists()
        assert not list(tmp_path.glob("*.part"))
    finally:
        api.scene.scene_dir = original


def test_terminal_imports_without_pty(monkeypatch):
    """terminal.py must import on a platform with no fcntl/openpty (Windows)."""
    import builtins
    import os as os_mod

    real_import = builtins.__import__

    def no_fcntl(name, *a, **k):
        if name == "fcntl":
            raise ImportError("No module named 'fcntl'")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", no_fcntl)
    monkeypatch.delattr(os_mod, "openpty", raising=False)
    for mod in [m for m in sys.modules if m.startswith("api.routes.terminal")]:
        del sys.modules[mod]

    import api.routes.terminal as term
    assert term._PTY_SUPPORTED is False
    assert term._master_fd is None


@pytest.mark.parametrize("path", [
    "packaging/rune-claude-server.spec",
    "packaging/entitlements.mac.plist",
    "packaging/icon.png",
    "scripts/build-backend.js",
    "scripts/setup-dev.sh",
    "scripts/setup-dev.ps1",
    "server_main.py",
    ".github/workflows/build.yml",
])
def test_packaging_files_present(path):
    assert (Path(__file__).parent.parent / path).exists(), f"missing {path}"


def test_spec_excludes_raw_data_bin():
    """The 26MB expanded buffer must not be bundled — only data.bin.gz is."""
    spec = (Path(__file__).parent.parent / "packaging/rune-claude-server.spec").read_text()
    assert '"data.bin"' in spec, "spec must exclude the raw data.bin"


def test_electron_spawns_backend_from_resources():
    """Packaged Electron must look for the backend in resourcesPath."""
    main = (Path(__file__).parent.parent / "electron/main.js").read_text()
    assert "process.resourcesPath" in main
    assert "app.isPackaged" in main


def test_renderer_uses_relative_api_urls():
    """Absolute localhost URLs break when the window loads 127.0.0.1."""
    api = (Path(__file__).parent.parent / "renderer/js/api.js").read_text()
    assert "http://localhost:7432" not in api
