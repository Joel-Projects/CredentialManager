import multiprocessing
import sys

# import psycogreen.gevent
#
# psycogreen.gevent.patch_psycopg()

access_log_format = '%(h)s %(l)s %(u)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
accesslog = "-"
bind = ":5000"
worker_class = "gthread"
capture_output = True
timeout = 86400
if sys.platform != "darwin":
    worker_tmp_dir = "/dev/shm"
threads = multiprocessing.cpu_count() * 4
wsgi_app = "app:create_app()"
