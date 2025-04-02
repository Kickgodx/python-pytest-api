import atexit
import logging
import multiprocessing
import os
from logging import FileHandler
from logging.handlers import QueueHandler, QueueListener

from filelock import FileLock

import config as cfg

os.makedirs(cfg.LOGS_PATH, exist_ok=True)

# Создаем файл лога, если он не существует или очищаем его, если он существует
log_file = os.path.join(cfg.LOGS_PATH, cfg.LOG_FILE_NAME)
with open(log_file, "w", encoding="utf-8") as f:
    f.write("")

logger = logging.getLogger(__name__)
logger.setLevel(cfg.FILE_LOG_LEVEL)

worker_id = os.environ.get("PYTEST_XDIST_WORKER", default="master")
formatter = logging.Formatter(f"[{worker_id.replace('gw', 'worker_')}]" + cfg.LOG_FORMAT)
formatter.datefmt = '[%H:%M:%S]'

# Блокировка для безопасной записи
file_lock = FileLock(f"{log_file}.lock")


# Кастомный FileHandler с блокировкой
class LockedFileHandler(FileHandler):
    def emit(self, record):
        with file_lock:
            super().emit(record)


file_log_handler = LockedFileHandler(str(log_file), "a", encoding="utf-8")
file_log_handler.setLevel(cfg.FILE_LOG_LEVEL)
file_log_handler.setFormatter(formatter)

queue = multiprocessing.Queue(-1)
queue_handler = QueueHandler(queue)
logger.addHandler(queue_handler)

# QueueListener с нормальным Handler, а не функцией
queue_listener = QueueListener(queue, file_log_handler)
queue_listener.start()


def shutdown_logger():
    queue_listener.stop()
    logger.removeHandler(queue_handler)
    queue.close()
    queue.join_thread()
    file_log_handler.close()
    if os.path.exists(f"{log_file}.lock"):
        os.remove(f"{log_file}.lock")


atexit.register(shutdown_logger)
