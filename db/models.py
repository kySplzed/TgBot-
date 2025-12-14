# db/models.py - модели данных для базы данных

from datetime import datetime
from typing import Optional

class User:
    """Модель пользователя"""
    def __init__(self, user_id: int, username: Optional[str] = None,
                 first_name: Optional[str] = None, last_name: Optional[str] = None,
                 language_code: Optional[str] = None, created_at: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.language_code = language_code
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'language_code': self.language_code,
            'created_at': self.created_at
        }

class Subscription:
    """Модель подписки"""
    def __init__(self, user_id: int, plan: str, plan_name: str, price: float,
                 start_date: str, end_date: str, status: str = 'active',
                 auto_renewal: bool = True, payment_id: Optional[str] = None):
        self.user_id = user_id
        self.plan = plan
        self.plan_name = plan_name
        self.price = price
        self.start_date = start_date
        self.end_date = end_date
        self.status = status  # active, expired, canceled
        self.auto_renewal = auto_renewal
        self.payment_id = payment_id

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'plan': self.plan,
            'plan_name': self.plan_name,
            'price': self.price,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'status': self.status,
            'auto_renewal': self.auto_renewal,
            'payment_id': self.payment_id
        }

class Payment:
    """Модель платежа"""
    def __init__(self, payment_id: str, user_id: int, plan: str, amount: float,
                 status: str = 'pending', created_at: Optional[str] = None,
                 confirmed_at: Optional[str] = None, yookassa_id: Optional[str] = None):
        self.payment_id = payment_id
        self.user_id = user_id
        self.plan = plan
        self.amount = amount
        self.status = status  # pending, succeeded, canceled, failed
        self.created_at = created_at or datetime.now().isoformat()
        self.confirmed_at = confirmed_at
        self.yookassa_id = yookassa_id

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'user_id': self.user_id,
            'plan': self.plan,
            'amount': self.amount,
            'status': self.status,
            'created_at': self.created_at,
            'confirmed_at': self.confirmed_at,
            'yookassa_id': self.yookassa_id
        }
