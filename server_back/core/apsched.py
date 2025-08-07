import datetime
import logging
import os
import subprocess
from pathlib import Path

from core import config

BACKUP_DIR = './backups'
KEEP_DAYS = 7

database_name = config.settings.PS_DATABASE_NAME
database_driver = config.settings.PS_DRIVER
database_username = config.settings.PS_USERNAME
database_password = config.settings.PS_PASSWORD
database_host = config.settings.PS_HOST
database_dbname = config.settings.PS_TABLE_NAME

errors_logger = logging.getLogger("errors")
actions_logger = logging.getLogger("actions")


def backup_postgres():
    Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now()
    filename = f"backup_{database_name}_{now.strftime('%Y%m%d_%H%M%S')}.sql"
    filepath = os.path.join(BACKUP_DIR, filename)

    env = os.environ.copy()
    env['PGPASSWORD'] = database_password

    try:
        subprocess.run([
            'pg_dump',
            '-h', database_host,
            '-p', str(5432),
            '-U', database_username,
            '-F', 'c',
            '-b',
            '-f', filepath,
            database_name
        ], env=env, check=True)
        actions_logger.info(f"[{now}] Backup created: {filepath}")
    except subprocess.CalledProcessError as e:
        errors_logger.info(f"[{now}] Backup failed: {e}")

    cleanup_old_backups()


def cleanup_old_backups():
    now = datetime.datetime.now()
    for file in os.listdir(BACKUP_DIR):
        if file.startswith(f"backup_{database_name}_") and file.endswith(".sql"):
            path = os.path.join(BACKUP_DIR, file)
            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            if (now - file_time).days >= KEEP_DAYS:
                os.remove(path)
                actions_logger.info(f"[{now}] Old backup deleted: {path}")
