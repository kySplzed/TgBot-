# handlers/subscription_flow.py - обработчики для подписок и платежей

from keyboards.inline_keyboards import get_subscription_keyboard, get_main_menu_keyboard
from services.payment_service import create_payment, process_payment_success
from services.subscription_service import get_user_subscription, get_subscription_status_text
from services.messages import SUBSCRIPTION_PLANS_TEXT
import time

def setup_subscription_handlers(bot):
    """Настройка обработчиков для подписок"""

    @bot.message_handler(commands=['subscribe'])
    def subscribe_command(message):
        markup = get_subscription_keyboard()
        bot.send_message(message.chat.id, SUBSCRIPTION_PLANS_TEXT,
                        reply_markup=markup)

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
            from services.subscription_service import activate_subscription

            activate_subscription(message.from_user.id, plan)
            process_payment_success(bot, f"test_payment_{message.from_user.id}")

            bot.reply_to(message, f"✅ Тестовый платеж обработан!\nПодписка {plan.upper()} активирована.")

        except Exception as e:
            bot.reply_to(message, f"Ошибка тестирования платежа: {str(e)}")

def setup_callback_handlers(bot):
    """Настройка обработчиков callback запросов"""

    @bot.callback_query_handler(func=lambda call: True)
    def callback_handler(call):
        if call.data == "product":
            from handlers.product_info import product_info
            product_info(bot, call)
        elif call.data == "pricing":
            from handlers.product_info import pricing_info
            pricing_info(bot, call)
        elif call.data == "status":
            subscription = get_user_subscription(call.from_user.id)
            status_text = get_subscription_status_text(subscription)

            markup = get_main_menu_keyboard()
            time.sleep(1)

            # Проверяем, нужно ли редактировать сообщение
            try:
                # Пытаемся получить информацию о текущем сообщении
                current_message = bot.get_message(call.message.chat.id, call.message.message_id)
                current_text = current_message.text
                current_markup = current_message.reply_markup

                # Если текст и разметка одинаковые, просто отвечаем на callback
                if current_text == status_text and str(current_markup) == str(markup):
                    bot.answer_callback_query(call.id, "Статус уже отображается")
                    return

                # Иначе редактируем сообщение
                bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    text=status_text,
                                    reply_markup=markup,
                                    parse_mode='Markdown')
            except Exception as e:
                # Если не можем получить сообщение, просто редактируем
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

            from services.messages import WELCOME_TEXT
            markup = get_main_menu_keyboard()
            bot.send_message(call.message.chat.id, WELCOME_TEXT, reply_markup=markup)
        elif call.data == "back":
            from handlers.product_info import back_to_main
            back_to_main(bot, call)
        elif call.data.startswith("subscribe_"):
            plan = call.data.split("_")[1]
            create_payment(bot, call, plan)
        elif call.data.startswith("pay_"):
            plan = call.data.split("_")[1]
            process_payment_success(bot, plan)
