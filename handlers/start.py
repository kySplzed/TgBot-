# handlers/start.py - обработчики команд start и основных команд

from keyboards.inline_keyboards import get_main_menu_keyboard, get_status_keyboard, get_delete_confirmation_keyboard
from keyboards.reply_keyboards import get_reply_keyboard
from services.subscription_service import get_user_subscription, get_subscription_status_text, cancel_subscription
from services.user_service import get_or_create_user
from services.messages import WELCOME_TEXT
from utils.logger import get_logger
import time

logger = get_logger(__name__)

def setup_start_handlers(bot):
    """Настройка обработчиков для команд start и основных"""

    @bot.message_handler(commands=['start'])
    def start(message):
        # Сохраняем/обновляем данные пользователя
        user = get_or_create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code
        )
        logger.info(f"User {user.user_id} started bot")

        # Очищаем историю сообщений при старте
        try:
            # Удаляем все сообщения в чате (кроме системных)
            for message_id in range(message.message_id - 10, message.message_id):
                try:
                    bot.delete_message(message.chat.id, message_id)
                except:
                    pass
        except Exception as e:
            logger.warning(f"Error clearing chat: {e}")

        markup = get_main_menu_keyboard()
        bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=markup)

    @bot.message_handler(commands=['status'])
    def status_command(message):
        # Обновляем данные пользователя
        get_or_create_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code
        )

        subscription = get_user_subscription(message.from_user.id)
        status_text = get_subscription_status_text(subscription)

        markup = get_status_keyboard()  # Используем клавиатуру статуса с кнопкой удаления
        bot.send_message(message.chat.id, status_text,
                        reply_markup=markup, parse_mode='Markdown')

    @bot.callback_query_handler(func=lambda call: call.data == "delete_subscription")
    def delete_subscription_callback(call):
        """Обработчик кнопки удаления подписки"""
        subscription = get_user_subscription(call.from_user.id)

        if not subscription or subscription.status != 'active':
            bot.answer_callback_query(call.id, "У вас нет активной подписки для удаления")
            return

        # Показываем сообщение с подтверждением
        warning_text = f"""
⚠️ **Внимание! Удаление подписки**

Вы собираетесь удалить подписку:
**{subscription.plan_name}** ({subscription.price}₽/месяц)

После удаления:
• Подписка станет недоступной
• Доступ к сервису прекратится
• Средства не возвращаются

Это действие нельзя отменить!
"""

        markup = get_delete_confirmation_keyboard()
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=warning_text,
                            reply_markup=markup,
                            parse_mode='Markdown')
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "confirm_delete")
    def confirm_delete_callback(call):
        """Обработчик подтверждения удаления подписки"""
        success = cancel_subscription(call.from_user.id)

        if success:
            result_text = """
✅ **Подписка удалена**

Ваша подписка была успешно отменена.
Доступ к сервису прекращен.
"""
            markup = get_main_menu_keyboard()
        else:
            result_text = """
❌ **Ошибка удаления**

Не удалось удалить подписку.
Возможно, у вас нет активной подписки.
"""
            markup = get_main_menu_keyboard()

        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=result_text,
                            reply_markup=markup,
                            parse_mode='Markdown')
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_delete")
    def cancel_delete_callback(call):
        """Обработчик отмены удаления подписки"""
        subscription = get_user_subscription(call.from_user.id)
        status_text = get_subscription_status_text(subscription)

        markup = get_status_keyboard()
        bot.edit_message_text(chat_id=call.message.chat.id,
                            message_id=call.message.message_id,
                            text=status_text,
                            reply_markup=markup,
                            parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Удаление отменено")
