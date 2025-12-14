# handlers/start.py - обработчики команд start и основных команд

from keyboards.inline_keyboards import get_main_menu_keyboard
from keyboards.reply_keyboards import get_reply_keyboard
from services.subscription_service import get_user_subscription, get_subscription_status_text
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

        markup = get_main_menu_keyboard()
        bot.send_message(message.chat.id, status_text,
                        reply_markup=markup, parse_mode='Markdown')
