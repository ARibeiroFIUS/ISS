# Configuração do Gunicorn otimizada para Render.com gratuito
import os

# Configurações básicas
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1  # Apenas 1 worker para economizar memória no plano gratuito
worker_class = "sync"
worker_connections = 50  # Reduzido para economizar recursos

# Timeouts otimizados para Render.com
timeout = 30  # 30 segundos máximo por request
keepalive = 2
max_requests = 100  # Reinicia worker após 100 requests para evitar memory leaks
max_requests_jitter = 10

# Configurações de memória
preload_app = True  # Carrega app antes de fazer fork dos workers
worker_tmp_dir = "/dev/shm"  # Usa RAM para arquivos temporários

# Logs
accesslog = "-"  # Log para stdout
errorlog = "-"   # Log para stderr
loglevel = "info"

# Configurações de processo
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Configurações específicas para Flask
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
} 