import multiprocessing

accesslog = "-"
bind = "127.0.0.1:5000"
timeout = 0
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
wsgi_app = "app:create_app()"
