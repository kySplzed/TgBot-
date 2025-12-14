# config.py - Конфигурация приложения

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# === TELEGRAM BOT ===
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'ВАШ_НАСТОЯЩИЙ_ТОКЕН_БОТА')

# === YOOKASSA PAYMENT ===
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', '1227929')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'test_nGg_nxAslebQ_bX-K2U43g8RK4XaejdPxsKQpVtqo8o')

# === APPLICATION SETTINGS ===
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development / production

# === WEBHOOK SETTINGS ===
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', 'localhost')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '5000'))
WEBHOOK_PATH = '/yookassa/webhook'

# === DATABASE ===
USERS_FILE = os.getenv('USERS_FILE', 'users.json')
SUBSCRIPTIONS_FILE = os.getenv('SUBSCRIPTIONS_FILE', 'subscriptions.json')
PAYMENTS_FILE = os.getenv('PAYMENTS_FILE', 'payments.json')

# === PLANS CONFIGURATION ===
PLANS = {
    'basic': {
        'price': 999,
        'name': 'Базовый тариф',
        'description': 'Основные функции продукта',
        'duration_days': 30
    },
    'premium': {
        'price': 1999,
        'name': 'Премиум тариф',
        'description': 'Расширенные возможности',
        'duration_days': 30
    },
    'vip': {
        'price': 3999,
        'name': 'VIP тариф',
        'description': 'Максимум преимуществ',
        'duration_days': 30
    }
}

# === LOGGING ===
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# === VALIDATION ===
MAX_MESSAGE_LENGTH = 4096
ALLOWED_PLANS = list(PLANS.keys())
