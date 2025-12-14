# logger.py - Настройка логирования

import logging
import sys
from config import LOG_LEVEL, LOG_FILE, DEBUG

def setup_logging():
    """Настройка логирования для всего приложения"""

    # Уровни логирования
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    level = log_levels.get(LOG_LEVEL.upper(), logging.INFO)

    # Форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Удаляем существующие обработчики
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Файловый обработчик (только для продакшена)
    if not DEBUG:
        try:
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            logging.warning(f"Не удалось настроить файловое логирование: {e}")

    # Настройка специфичных логгеров
    logging.getLogger('telebot').setLevel(logging.WARNING)  # Уменьшаем verbosity telebot
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Уменьшаем verbosity Flask
    logging.getLogger('yookassa').setLevel(logging.INFO)

    logging.info("Логирование настроено успешно")
    logging.info(f"Уровень логирования: {LOG_LEVEL}")
    logging.info(f"Файл логов: {LOG_FILE}")
    logging.info(f"Режим отладки: {DEBUG}")

def get_logger(name: str) -> logging.Logger:
    """Получить логгер для конкретного модуля"""
    return logging.getLogger(name)
