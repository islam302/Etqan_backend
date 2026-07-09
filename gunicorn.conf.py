"""Gunicorn configuration for the ETQAN backend.

Tuned for running inside containers (Docker Desktop / WSL2 / cloud). The key
setting is ``worker_tmp_dir = "/dev/shm"``: gunicorn writes each worker's
heartbeat to a temp file, and on slow overlay/WSL2 filesystems that stalls
under I/O load and triggers spurious "WORKER TIMEOUT ... (no URI read)" kills.
Putting the heartbeat in shared memory (tmpfs) avoids that.

Override any value with the matching ``GUNICORN_*`` environment variable.
"""
from __future__ import annotations

import multiprocessing
import os

# Bind / networking
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")

# Worker processes. Default to a sensible CPU-based count, capped so small
# containers don't over-subscribe; override with GUNICORN_WORKERS.
_default_workers = min((multiprocessing.cpu_count() * 2) + 1, 4)
workers = int(os.environ.get("GUNICORN_WORKERS", _default_workers))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")
threads = int(os.environ.get("GUNICORN_THREADS", "2"))

# Heartbeat file in shared memory — prevents false worker timeouts in Docker.
# Fall back to the default location if /dev/shm is unavailable (e.g. Windows).
worker_tmp_dir = "/dev/shm" if os.path.isdir("/dev/shm") else None

# Timeouts (seconds). Generous request timeout to tolerate slow container I/O.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "5"))

# Recycle workers periodically to bound memory growth.
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "100"))

# Logging to stdout/stderr so container log drivers capture it.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
