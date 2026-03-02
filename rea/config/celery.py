import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent          # rea/config/
rea_dir = current_dir.parent                  # rea/
project_root = rea_dir.parent                  # rea-app/ (где лежат rea_users, rea_auth и т.д.)

# Добавляем оба пути в sys.path
for path in [str(project_root), str(rea_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('rea')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()