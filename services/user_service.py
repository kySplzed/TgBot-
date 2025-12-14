# services/user_service.py - бизнес-логика для работы с пользователями

from db.database import get_or_create_user as db_get_or_create_user, get_statistics as db_get_statistics, get_user_subscription as db_get_user_subscription, save_user
from db.models import User

def get_or_create_user(user_id: int, username=None, first_name=None, last_name=None, language_code=None):
    """Получить или создать пользователя"""
    return db_get_or_create_user(user_id, username, first_name, last_name, language_code)

def get_user_info(user_id: int):
    """Получить информацию о пользователе"""
    subscription = db_get_user_subscription(user_id)
    user = get_or_create_user(user_id)
    return {
        'user': user,
        'subscription': subscription
    }

def update_user_info(user_id: int, **kwargs):
    """Обновить информацию о пользователе"""
    user = get_or_create_user(user_id)
    # Обновляем поля пользователя
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    save_user(user)

def is_admin(user_id: int):
    """Проверить, является ли пользователь администратором"""
    # Список администраторов можно хранить в конфиге или БД
    admins = []  # Пока что пустой список
    return user_id in admins

def get_user_statistics():
    """Получить статистику по пользователям"""
    return db_get_statistics()
