# handlers/__init__.py

from .start import setup_start_handlers
from .product_info import setup_product_handlers
from .subscription_flow import setup_subscription_handlers, setup_callback_handlers
from .payment_processing import setup_payment_handlers
from .admin import setup_admin_handlers

def setup_handlers(bot):
    """Настройка всех обработчиков бота"""
    setup_start_handlers(bot)
    setup_product_handlers(bot)
    setup_subscription_handlers(bot)
    setup_callback_handlers(bot)
    setup_payment_handlers(bot)
    setup_admin_handlers(bot)
