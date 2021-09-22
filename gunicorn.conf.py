import multiprocessing
# import logging
# import os
#
# log = logging.getLogger(__name__)
#
# HOSTNAME = os.getenv("HOSTNAME")
# if not HOSTNAME:
#     log.error("HOSTNAME not set! Exiting...")
#     exit(1)
#
# APP_HOME = os.getenv("APP_HOME")
# if not APP_HOME:
#     log.error("APP_HOME not set! Exiting...")
#     exit(1)

accesslog = "-"
bind = "0.0.0.0:5000"
# certfile = f"/etc/letsencrypt/live/{HOSTNAME}/fullchain.pem"
# keyfile = f"/etc/letsencrypt/live/{HOSTNAME}/privkey.pem"
timeout = 3605
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
# umask = 0o07
