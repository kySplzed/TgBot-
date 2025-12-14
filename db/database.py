# db/database.py - функции для работы с базой данных

import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from .models import User, Subscription, Payment

# Файлы для хранения данных
USERS_FILE = os.getenv('USERS_FILE', 'users.json')
SUBSCRIPTIONS_FILE = os.getenv('SUBSCRIPTIONS_FILE', 'subscriptions.json')
PAYMENTS_FILE = os.getenv('PAYMENTS_FILE', 'payments.json')

def init_database():
    """Инициализация базы данных"""
    for file_path in [USERS_FILE, SUBSCRIPTIONS_FILE, PAYMENTS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

def _load_json_file(file_path: str) -> Dict:
    """Загрузка JSON файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def _save_json_file(file_path: str, data: Dict):
    """Сохранение JSON файла"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ =====

def save_user(user: User):
    """Сохранение пользователя"""
    users = _load_json_file(USERS_FILE)
    users[str(user.user_id)] = user.to_dict()
    _save_json_file(USERS_FILE, users)

def get_user(user_id: int) -> Optional[User]:
    """Получение пользователя по ID"""
    users = _load_json_file(USERS_FILE)
    user_data = users.get(str(user_id))
    if user_data:
        return User(**user_data)
    return None

def get_or_create_user(user_id: int, username: Optional[str] = None,
                      first_name: Optional[str] = None, last_name: Optional[str] = None,
                      language_code: Optional[str] = None) -> User:
    """Получение или создание пользователя"""
    user = get_user(user_id)
    if user:
        # Обновляем данные пользователя если они изменились
        updated = False
        if username and user.username != username:
            user.username = username
            updated = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        if language_code and user.language_code != language_code:
            user.language_code = language_code
            updated = True

        if updated:
            save_user(user)
        return user
    else:
        # Создаем нового пользователя
        user = User(user_id, username, first_name, last_name, language_code)
        save_user(user)
        return user

def get_all_users() -> List[User]:
    """Получение всех пользователей"""
    users = _load_json_file(USERS_FILE)
    return [User(**user_data) for user_data in users.values()]

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОДПИСКАМИ =====

def save_subscription(subscription: Subscription):
    """Сохранение подписки"""
    subscriptions = _load_json_file(SUBSCRIPTIONS_FILE)
    subscriptions[str(subscription.user_id)] = subscription.to_dict()
    _save_json_file(SUBSCRIPTIONS_FILE, subscriptions)

def get_user_subscription(user_id: int) -> Optional[Subscription]:
    """Получение подписки пользователя"""
    subscriptions = _load_json_file(SUBSCRIPTIONS_FILE)
    sub_data = subscriptions.get(str(user_id))
    if sub_data:
        return Subscription(**sub_data)
    return None

def check_expired_subscriptions() -> int:
    """Проверка и обновление истекших подписок. Возвращает количество обновленных подписок."""
    subscriptions = _load_json_file(SUBSCRIPTIONS_FILE)
    updated_count = 0

    for user_id, sub in subscriptions.items():
        if sub['status'] == 'active':
            end_date = datetime.fromisoformat(sub['end_date'])
            if end_date < datetime.now():
                sub['status'] = 'expired'
                updated_count += 1

    if updated_count > 0:
        _save_json_file(SUBSCRIPTIONS_FILE, subscriptions)

    return updated_count

# ===== ФУНКЦИИ ДЛЯ РАБОТЫ С ПЛАТЕЖАМИ =====

def save_payment(payment: Payment):
    """Сохранение платежа"""
    payments = _load_json_file(PAYMENTS_FILE)
    payments[payment.payment_id] = payment.to_dict()
    _save_json_file(PAYMENTS_FILE, payments)

def get_payment(payment_id: str) -> Optional[Payment]:
    """Получение платежа по ID"""
    payments = _load_json_file(PAYMENTS_FILE)
    payment_data = payments.get(payment_id)
    if payment_data:
        return Payment(**payment_data)
    return None

def update_payment_status(payment_id: str, status: str, confirmed_at: Optional[str] = None) -> bool:
    """Обновление статуса платежа"""
    payments = _load_json_file(PAYMENTS_FILE)
    if payment_id in payments:
        payments[payment_id]['status'] = status
        if confirmed_at:
            payments[payment_id]['confirmed_at'] = confirmed_at
        _save_json_file(PAYMENTS_FILE, payments)
        return True
    return False

def get_user_payments(user_id: int) -> List[Payment]:
    """Получение всех платежей пользователя"""
    payments = _load_json_file(PAYMENTS_FILE)
    user_payments = []
    for payment_data in payments.values():
        if payment_data['user_id'] == user_id:
            user_payments.append(Payment(**payment_data))
    return user_payments

def get_pending_payments() -> List[Payment]:
    """Получение платежей со статусом pending"""
    payments = _load_json_file(PAYMENTS_FILE)
    pending_payments = []
    for payment_data in payments.values():
        if payment_data['status'] == 'pending':
            pending_payments.append(Payment(**payment_data))
    return pending_payments

# ===== СТАТИСТИКА =====

def get_statistics() -> Dict:
    """Получение общей статистики"""
    users = get_all_users()
    subscriptions = _load_json_file(SUBSCRIPTIONS_FILE)
    payments = _load_json_file(PAYMENTS_FILE)

    active_subscriptions = sum(1 for sub in subscriptions.values() if sub['status'] == 'active')
    total_payments = len(payments)
    successful_payments = sum(1 for p in payments.values() if p['status'] == 'succeeded')

    return {
        'total_users': len(users),
        'active_subscriptions': active_subscriptions,
        'total_payments': total_payments,
        'successful_payments': successful_payments,
        'failed_payments': sum(1 for p in payments.values() if p['status'] == 'failed')
    }
