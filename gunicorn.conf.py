import multiprocessing
import psycogreen.gevent

psycogreen.gevent.patch_psycopg()

accesslog = "-"
bind = ":5000"
worker_class = "gevent"
timeout = 900
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
