import logging
import multiprocessing
import os

log = logging.getLogger(__name__)

HOSTNAME = os.getenv("HOSTNAME")
if not HOSTNAME:
    log.error("HOSTNAME not set! Exiting...")
    exit(1)

accesslog = "-"
bind = ":443"
certfile = f"/etc/letsencrypt/live/{HOSTNAME}/fullchain.pem"
keyfile = f"/etc/letsencrypt/live/{HOSTNAME}/privkey.pem"
timeout = 3605
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
