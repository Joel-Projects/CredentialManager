import multiprocessing

accesslog = "-"
bind = "0.0.0.0:5000"
timeout = 3605
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
