import multiprocessing

workers = 1 # multiprocessing.cpu_count() * 2 + 1  # Número de workers baseados no número de CPUs
threads = 2
bind = "0.0.0.0:8000" 
worker_class = "uvicorn.workers.UvicornWorker"  # Usa Uvicorn para executar a API
timeout = 120 
loglevel = "info"
