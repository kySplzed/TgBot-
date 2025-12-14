# handlers.py - обработчики команд и событий

from messages import (
    WELCOME_TEXT, PRODUCT_INFO_TEXT, PRICING_TEXT,
    SUBSCRIPTION_PLANS_TEXT
)
from keyboards import (
    get_main_menu_keyboard, get_product_keyboard, get_pricing_keyboard,
    get_subscription_keyboard, get_reply_keyboard
)
from payments import create_payment, process_payment_success
from config import PLANS
from subscription import get_user_subscription, get_subscription_status_text, cancel_subscription
import time

def setup_handlers(bot):
    """Настройка всех обработчиков"""

    @bot.message_handler(commands=['start'])
    def start(message):
        # Очищаем историю сообщений при старте
        try:
            # Удаляем все сообщения в чате (кроме системных)
            for message_id in range(message.message_id - 10, message.message_id):
                try:
                    bot.delete_message(message.chat.id, message_id)
                except:
                    pass
        except Exception as e:
            print(f"Error clearing chat: {e}")

        markup = get_main_menu_keyboard()
        bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        if call.data == "product":
            product_info(bot, call)
        elif call.data == "pricing":
            pricing_info(bot, call)
        elif call.data == "status":
            subscription = get_user_subscription(call.from_user.id)
            status_text = get_subscription_status_text(subscription)

            markup = get_main_menu_keyboard()
            time.sleep(1)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                text=status_text,
                                reply_markup=markup,
                                parse_mode='Markdown')
        elif call.data == "main_menu":
            # Очистка сообщений и возврат в главное меню
            try:
                # Удаляем все сообщения в чате (кроме системных)
                for message_id in range(call.message.message_id - 10, call.message.message_id + 1):
                    try:
                        bot.delete_message(call.message.chat.id, message_id)
                    except:
                        pass
            except Exception as e:
                print(f"Error clearing chat: {e}")

            markup = get_main_menu_keyboard()
            bot.send_message(call.message.chat.id, WELCOME_TEXT, reply_markup=markup)
        elif call.data == "back":
            back_to_main(bot, call)
        elif call.data.startswith("subscribe_"):
            plan = call.data.split("_")[1]
            create_payment(bot, call, plan)
        elif call.data.startswith("pay_"):
            plan = call.data.split("_")[1]
            process_payment_success(bot, plan)


    @bot.message_handler(commands=['product'])
    def product_command(message):
        markup = get_product_keyboard()
        bot.send_message(message.chat.id, PRODUCT_INFO_TEXT,
                        reply_markup=markup, parse_mode='Markdown')

    @bot.message_handler(commands=['pricing'])
    def pricing_command(message):
        markup = get_pricing_keyboard()
        bot.send_message(message.chat.id, PRICING_TEXT,
                        reply_markup=markup, parse_mode='Markdown')

    @bot.message_handler(commands=['subscribe'])
    def subscribe_command(message):
        markup = get_subscription_keyboard()
        bot.send_message(message.chat.id, SUBSCRIPTION_PLANS_TEXT,
                        reply_markup=markup)

    @bot.message_handler(commands=['status'])
    def status_command(message):
        subscription = get_user_subscription(message.from_user.id)
        status_text = get_subscription_status_text(subscription)

        markup = get_main_menu_keyboard()
        bot.send_message(message.chat.id, status_text,
                        reply_markup=markup, parse_mode='Markdown')

    @bot.message_handler(commands=['testpay'])
    def test_payment_command(message):
        """Тестовая команда для имитации оплаты"""
        # Разбираем аргументы команды: /testpay basic или /testpay premium или /testpay vip
        try:
            args = message.text.split()
            if len(args) < 2:
                bot.reply_to(message, "Использование: /testpay <basic|premium|vip>\nПример: /testpay basic")
                return

            plan = args[1].lower()
            if plan not in ['basic', 'premium', 'vip']:
                bot.reply_to(message, "Неверный план. Используйте: basic, premium или vip")
                return

            # Имитируем успешный платеж
            from subscription import activate_subscription
            from payments import process_payment_success

            activate_subscription(message.from_user.id, plan)
            process_payment_success(bot, f"test_payment_{message.from_user.id}")

            bot.reply_to(message, f"✅ Тестовый платеж обработан!\nПодписка {plan.upper()} активирована.")

        except Exception as e:
            bot.reply_to(message, f"Ошибка тестирования платежа: {str(e)}")



def product_info(bot, call):
    """Показать информацию о продукте"""
    markup = get_product_keyboard()

    if hasattr(call, 'data'):  # Это callback query
        time.sleep(1)  # Задержка 1 секунда
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=PRODUCT_INFO_TEXT,
                            parse_mode='Markdown',
                            reply_markup=markup)
    else:  # Это обычное сообщение
        bot.send_message(call.chat.id, PRODUCT_INFO_TEXT,
                        reply_markup=markup, parse_mode='Markdown')

def pricing_info(bot, call):
    """Показать цены и тарифы"""
    markup = get_pricing_keyboard()

    if hasattr(call, 'data'):  # Это callback query
        time.sleep(1)  # Задержка 1 секунда
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=PRICING_TEXT,
                            parse_mode='Markdown',
                            reply_markup=markup)
    else:  # Это обычное сообщение
        bot.send_message(call.chat.id, PRICING_TEXT,
                        reply_markup=markup, parse_mode='Markdown')

def back_to_main(bot, call):
    """Возврат в главное меню"""
    markup = get_main_menu_keyboard()

    time.sleep(1)  # Задержка 1 секунда
    bot.edit_message_text(chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=WELCOME_TEXT,
                        reply_markup=markup)
