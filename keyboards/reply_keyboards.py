# keyboards/reply_keyboards.py - Reply клавиатуры бота

from telebot import types

def get_reply_keyboard():
    """Reply клавиатура для меню Telegram"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    product_btn = types.KeyboardButton("📦 О продукте")
    pricing_btn = types.KeyboardButton("💰 Цены")
    status_btn = types.KeyboardButton("📊 Мой статус")
    subscribe_btn = types.KeyboardButton("🎯 Подписка")
    support_btn = types.KeyboardButton("🆘 Поддержка")
    markup.add(product_btn, pricing_btn, status_btn, subscribe_btn, support_btn)
    return markup
