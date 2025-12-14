# services/payment_service.py - бизнес-логика для обработки платежей

import uuid
from datetime import datetime
from typing import Optional, Tuple
import yookassa
from yookassa import Payment
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, PLANS
from keyboards.inline_keyboards import get_payment_keyboard, get_success_keyboard, get_main_menu_keyboard
from services.messages import get_payment_text, get_success_text, get_payment_error_text
from services.subscription_service import activate_subscription
from db.database import save_payment, get_payment, update_payment_status
from db.models import Payment as PaymentModel
from utils.logger import get_logger

# Настройка YooKassa
yookassa.Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)

# Хранение активных платежей (в реальном приложении использовать БД)
active_payments = {}

logger = get_logger(__name__)

def create_payment(bot, call, plan: str) -> Optional[str]:
    """Создание платежа через YooKassa. Возвращает payment_id или None при ошибке."""

    if plan not in PLANS:
        bot.answer_callback_query(call.id, "Неверный план подписки")
        return None

    plan_info = PLANS[plan]
    payment_id = str(uuid.uuid4())

    try:
        # Создаем платеж через YooKassa
        yookassa_payment = Payment.create({
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
                "payment_id": payment_id,
                "user_id": call.from_user.id,
                "plan": plan,
                "chat_id": call.message.chat.id,
                "message_id": call.message.message_id
            }
        })

        # Сохраняем информацию о платеже в БД
        payment = PaymentModel(
            payment_id=payment_id,
            user_id=call.from_user.id,
            plan=plan,
            amount=plan_info['price'],
            status='pending',
            yookassa_id=yookassa_payment.id
        )
        save_payment(payment)

        # Сохраняем информацию о активном платеже для быстрого доступа
        active_payments[payment_id] = {
            "user_id": call.from_user.id,
            "plan": plan,
            "chat_id": call.message.chat.id,
            "message_id": call.message.message_id,
            "yookassa_id": yookassa_payment.id
        }

        payment_url = yookassa_payment.confirmation.confirmation_url
        payment_text = get_payment_text(plan_info['name'], plan_info['price'], plan_info['description'])

        markup = get_payment_keyboard(payment_url)

        import time
        time.sleep(1)  # Задержка 1 секунда
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=payment_text,
                            parse_mode='Markdown',
                            reply_markup=markup)

        logger.info(f"Payment {payment_id} created for user {call.from_user.id}, plan {plan}")
        return payment_id

    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        bot.answer_callback_query(call.id, f"Ошибка создания платежа: {str(e)}")
        return None

def process_payment_success(bot, payment_id: str) -> bool:
    """Обработка успешного платежа. Возвращает True при успехе."""

    # Сначала проверяем активные платежи
    payment_info = active_payments.get(payment_id)

    # Если не нашли в активных, ищем в базе данных
    if not payment_info:
        payment = get_payment(payment_id)
        if payment and payment.status == 'pending':
            # Создаем информацию о платеже для обработки
            payment_info = {
                'user_id': payment.user_id,
                'plan': payment.plan,
                'chat_id': payment.user_id,  # Используем user_id как chat_id для простоты
                'message_id': None  # Не можем определить message_id из БД
            }
        else:
            logger.warning(f"Payment {payment_id} not found in active payments or database")
            return False

    # Обновляем статус платежа в БД
    confirmed_at = datetime.now().isoformat()
    if not update_payment_status(payment_id, 'succeeded', confirmed_at):
        logger.error(f"Failed to update payment {payment_id} status")
        return False

    plan = payment_info['plan']
    success_text = get_success_text(plan)
    markup = get_success_keyboard()

    try:
        if payment_info.get('message_id'):
            # Если есть message_id, редактируем сообщение
            bot.edit_message_text(chat_id=payment_info['chat_id'],
                                message_id=payment_info['message_id'],
                                text=success_text,
                                parse_mode='Markdown',
                                reply_markup=markup)
        else:
            # Если нет message_id, отправляем новое сообщение
            bot.send_message(chat_id=payment_info['chat_id'],
                           text=success_text,
                           parse_mode='Markdown',
                           reply_markup=markup)
    except Exception as e:
        logger.error(f"Error sending payment success message: {e}")

    # Активируем подписку
    try:
        activate_subscription(payment_info['user_id'], plan, payment_id)
        logger.info(f"Subscription activated for user {payment_info['user_id']}, plan {plan}")
    except Exception as e:
        logger.error(f"Error activating subscription: {e}")

    # Удаляем из активных платежей, если он там был
    if payment_id in active_payments:
        del active_payments[payment_id]

    return True

def process_payment_error(bot, payment_id: str, error_message: str = None) -> bool:
    """Обработка ошибки платежа. Возвращает True при успехе."""

    payment_info = active_payments.get(payment_id)
    if not payment_info:
        logger.warning(f"Payment {payment_id} not found in active payments")
        return False

    # Обновляем статус платежа в БД
    if not update_payment_status(payment_id, 'failed'):
        logger.error(f"Failed to update payment {payment_id} status")
        return False

    error_text = get_payment_error_text(error_message or "Неизвестная ошибка")
    markup = get_main_menu_keyboard()

    try:
        bot.edit_message_text(chat_id=payment_info['chat_id'],
                            message_id=payment_info['message_id'],
                            text=error_text,
                            parse_mode='Markdown',
                            reply_markup=markup)
    except Exception as e:
        logger.error(f"Error updating payment error message: {e}")

    # Удаляем из активных платежей
    del active_payments[payment_id]

    return True

def check_payment_status(payment_id: str) -> Optional[str]:
    """Проверка статуса платежа в YooKassa"""

    try:
        payment = Payment.find_one(payment_id)
        return payment.status
    except Exception as e:
        logger.error(f"Error checking payment status: {e}")
        return None

def process_webhook_payment_succeeded(payment_data: dict) -> bool:
    """Обработка webhook уведомления об успешном платеже"""

    try:
        metadata = payment_data.get('metadata', {})
        payment_id = metadata.get('payment_id')

        if not payment_id:
            logger.error("No payment_id in webhook metadata")
            return False

        # Проверяем, что YooKassa сообщает о успешном платеже
        event = payment_data.get('event')
        if event != 'payment.succeeded':
            logger.warning(f"Unexpected event: {event}, expected payment.succeeded")
            return False

        # Получаем информацию о платеже из нашей БД
        payment = get_payment(payment_id)
        if not payment:
            logger.error(f"Payment {payment_id} not found in database")
            return False

        # Если платеж еще не обработан
        if payment.status == 'pending':
            # Обновляем статус платежа
            confirmed_at = datetime.now().isoformat()
            update_payment_status(payment_id, 'succeeded', confirmed_at)

            # Активируем подписку
            activate_subscription(payment.user_id, payment.plan, payment_id)

            logger.info(f"Payment {payment_id} processed successfully via webhook")
            return True
        else:
            logger.info(f"Payment {payment_id} already processed")
            return True

    except Exception as e:
        logger.error(f"Error processing webhook payment succeeded: {e}")
        return False

def process_webhook_payment_failed(payment_data: dict) -> bool:
    """Обработка webhook уведомления о неудачном платеже"""

    try:
        metadata = payment_data.get('metadata', {})
        payment_id = metadata.get('payment_id')

        if not payment_id:
            logger.error("No payment_id in webhook metadata")
            return False

        # Обновляем статус платежа
        update_payment_status(payment_id, 'failed')

        logger.info(f"Payment {payment_id} marked as failed via webhook")
        return True

    except Exception as e:
        logger.error(f"Error processing webhook payment failed: {e}")
        return False
