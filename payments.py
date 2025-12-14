# payments.py - функции оплаты и подписок

import yookassa
from yookassa import Payment
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, PLANS
from keyboards import get_payment_keyboard, get_success_keyboard
from messages import get_payment_text, get_success_text
from subscription import activate_subscription
import time

# Настройка YooKassa
yookassa.Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

# Хранение активных платежей (в реальном приложении использовать БД)
active_payments = {}

def create_payment(bot, call, plan):
    """Создание платежа через YooKassa"""

    if plan not in PLANS:
        bot.answer_callback_query(call.id, "Неверный план подписки")
        return

    plan_info = PLANS[plan]

    try:
        # Создаем платеж через YooKassa
        payment = Payment.create({
            "amount": {
                "value": str(plan_info['price']),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/" + str(call.message.chat.username) if call.message.chat.username else "https://telegram.org"
            },
            "capture": True,
            "description": f"Оплата подписки: {plan_info['name']}",
            "metadata": {
                "user_id": call.from_user.id,
                "plan": plan,
                "chat_id": call.message.chat.id,
                "message_id": call.message.message_id
            }
        })

        # Сохраняем информацию о платеже
        active_payments[payment.id] = {
            "user_id": call.from_user.id,
            "plan": plan,
            "chat_id": call.message.chat.id,
            "message_id": call.message.message_id,
            "status": "pending"
        }

        payment_url = payment.confirmation.confirmation_url
        payment_text = get_payment_text(plan_info['name'], plan_info['price'], plan_info['description'])

        markup = get_payment_keyboard(payment_url)

        time.sleep(1)  # Задержка 1 секунда
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=payment_text,
                            parse_mode='Markdown',
                            reply_markup=markup)

    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка создания платежа: {str(e)}")
        print(f"Payment creation error: {e}")

def process_payment_success(bot, payment_id):
    """Обработка успешного платежа"""

    if payment_id not in active_payments:
        print(f"Payment {payment_id} not found in active payments")
        return

    payment_info = active_payments[payment_id]
    plan = payment_info['plan']

    success_text = get_success_text(plan)
    markup = get_success_keyboard()

    try:
        bot.edit_message_text(chat_id=payment_info['chat_id'],
                            message_id=payment_info['message_id'],
                            text=success_text,
                            parse_mode='Markdown',
                            reply_markup=markup)
    except Exception as e:
        print(f"Error updating payment message: {e}")

    # Удаляем из активных платежей
    del active_payments[payment_id]

def check_payment_status(payment_id):
    """Проверка статуса платежа (для webhook или периодической проверки)"""

    try:
        payment = Payment.find_one(payment_id)
        return payment.status
    except Exception as e:
        print(f"Error checking payment status: {e}")
        return None

def get_user_subscriptions(user_id):
    """Получение активных подписок пользователя (заглушка)"""
    # В реальном приложении здесь будет запрос к БД
    return []

def cancel_subscription(user_id, plan):
    """Отмена подписки (заглушка)"""
    # В реальном приложении здесь будет логика отмены
    pass
