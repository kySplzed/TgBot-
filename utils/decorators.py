# utils/decorators.py - декораторы для бота

import functools
from utils.logger import get_logger

logger = get_logger(__name__)

def admin_required(func):
    """Декоратор для проверки прав администратора"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Здесь можно добавить проверку на администратора
        # Пока что просто логируем
        logger.info(f"Admin function called: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def subscription_required(func):
    """Декоратор для проверки активной подписки"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Здесь можно добавить проверку подписки
        # Пока что просто логируем
        logger.info(f"Subscription required function called: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def rate_limit(limit=5, period=60):
    """Декоратор для ограничения частоты вызовов"""
    def decorator(func):
        # Простая реализация rate limiting
        # В реальном приложении лучше использовать Redis или другую БД
        calls = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем идентификатор пользователя (предполагаем, что первый аргумент - message или call)
            user_id = None
            if args and hasattr(args[0], 'from_user'):
                user_id = args[0].from_user.id
            elif args and hasattr(args[0], 'message') and hasattr(args[0].message, 'from_user'):
                user_id = args[0].message.from_user.id

            if user_id:
                import time
                current_time = time.time()

                if user_id not in calls:
                    calls[user_id] = []

                # Очищаем старые вызовы
                calls[user_id] = [t for t in calls[user_id] if current_time - t < period]

                if len(calls[user_id]) >= limit:
                    logger.warning(f"Rate limit exceeded for user {user_id}")
                    return None

                calls[user_id].append(current_time)

            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_execution(func):
    """Декоратор для логирования выполнения функций"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Executing {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Successfully executed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            raise
    return wrapper
