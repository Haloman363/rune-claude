"""Persistent bash PTY WebSocket endpoint."""
import fcntl
import os
import queue
import re
import select
import subprocess
import threading

from flask import Blueprint
from flask_sock import Sock

sock = Sock()
bp = Blueprint("terminal", __name__)


def init_sock(app):
    sock.init_app(app)


# PTY singleton — spawned once at import time
_master_fd, _slave_fd = os.openpty()
os.set_inheritable(_slave_fd, True)
_pty_proc = subprocess.Popen(
    ["/bin/bash", "--login"],
    stdin=_slave_fd,
    stdout=_slave_fd,
    stderr=_slave_fd,
    close_fds=True,
    start_new_session=True,
)
os.close(_slave_fd)
_flags = fcntl.fcntl(_master_fd, fcntl.F_GETFL)
fcntl.fcntl(_master_fd, fcntl.F_SETFL, _flags | os.O_NONBLOCK)

_ANSI = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
_OSC  = re.compile(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)')
_CTRL = re.compile(r'[\x00-\x08\x0b-\x1f\x7f]')
_PROMPT = re.compile(r'.*[@#]\S*:.*\$')

# Broadcast output to all connected clients
_subscribers: list = []
_subscribers_lock = threading.Lock()


def _broadcast(line: str) -> None:
    with _subscribers_lock:
        for q in _subscribers:
            q.put(line)


def _reader():
    buf = ""
    while True:
        r, _, _ = select.select([_master_fd], [], [], 0.05)
        if not r:
            continue
        try:
            chunk = os.read(_master_fd, 4096).decode("utf-8", errors="replace")
        except OSError:
            break
        chunk = _OSC.sub("", chunk)
        chunk = _ANSI.sub("", chunk)
        chunk = _CTRL.sub("", chunk)
        buf += chunk
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.rstrip("\r").strip()
            if line and not _PROMPT.match(line):
                _broadcast(line)


threading.Thread(target=_reader, daemon=True).start()


_ALLOWED_ORIGINS = {"http://localhost:7432", "file://", "null"}


@sock.route("/ws/terminal", bp=bp)
def terminal_ws(ws):
    from flask import request as flask_request
    from simple_websocket import ConnectionClosed as WsClosed
    origin = flask_request.headers.get("Origin", "null")
    if origin not in _ALLOWED_ORIGINS:
        ws.close(message=b"forbidden")
        return
    my_q: queue.Queue[str] = queue.Queue()
    with _subscribers_lock:
        _subscribers.append(my_q)
    try:
        while True:
            while True:
                try:
                    ws.send(my_q.get_nowait())
                except queue.Empty:
                    break
            try:
                msg = ws.receive(timeout=0.1)
                if msg is not None:
                    os.write(_master_fd, (msg + "\n").encode("utf-8"))
            except WsClosed:
                break
            except Exception:
                pass
    finally:
        with _subscribers_lock:
            _subscribers.remove(my_q)
