# handlers/product_info.py - обработчики для информации о продукте и ценах

from keyboards.inline_keyboards import get_product_keyboard, get_pricing_keyboard, get_main_menu_keyboard
from services.messages import PRODUCT_INFO_TEXT, PRICING_TEXT
import time

def setup_product_handlers(bot):
    """Настройка обработчиков для продукта и цен"""

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
    from services.messages import WELCOME_TEXT
    markup = get_main_menu_keyboard()

    time.sleep(1)  # Задержка 1 секунда
    bot.edit_message_text(chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=WELCOME_TEXT,
                        reply_markup=markup)
