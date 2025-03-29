import logging
import os
from logging import FileHandler

import config as cfg

os.makedirs(cfg.LOGS_PATH, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(cfg.FILE_LOG_LEVEL)

worker_id = os.environ.get("PYTEST_XDIST_WORKER", default="master")
formatter = logging.Formatter(f"{worker_id}: " + cfg.LOG_FORMAT)
formatter.datefmt = '%H:%M:%S'

log_file = os.path.join(cfg.LOGS_PATH, cfg.LOG_FILE_NAME)
file_log_handler = FileHandler(str(log_file), "w", "utf-8")
file_log_handler.setLevel(cfg.FILE_LOG_LEVEL)
file_log_handler.setFormatter(formatter)

# queue = multiprocessing.Queue(-1)
# queue_handler = QueueHandler(queue)

logger.addHandler(file_log_handler)
# logger.addHandler(queue_handler)

# Слушатель очереди
# queue_listener = QueueListener(queue, file_log_handler)
#
# # Запускаем слушатель очереди
# queue_listener.start()

# Функция для завершения логгера
# def shutdown_logger():
#     """Завершает работу логгера и очищает ресурсы."""
#     queue_listener.stop()  # Останавливаем слушатель очереди
#     logger.removeHandler(queue_handler)  # Удаляем хендлер
#     queue.close()  # Закрываем очередь
#     queue.join_thread()  # Ожидаем завершения потока очереди
#     file_log_handler.close()  # Закрываем файловый хендлер
#
# # Регистрируем shutdown_logger для вызова при завершении работы
# atexit.register(shutdown_logger)
