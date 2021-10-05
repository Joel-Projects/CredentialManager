import multiprocessing
import sys

import psycogreen.gevent

psycogreen.gevent.patch_psycopg()

access_log_format = '%(h)s %(l)s %(u)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
accesslog = "-"
bind = ":5000"
worker_class = "gevent"
capture_output = True
timeout = 900
if sys.platform != "darwin":
    worker_tmp_dir = "/dev/shm"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
