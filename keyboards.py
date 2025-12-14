# keyboards.py - клавиатуры бота

from telebot import types

def get_main_menu_keyboard():
    """Главная клавиатура с основными кнопками"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    product_btn = types.InlineKeyboardButton("📦 Подробная информация о продукте", callback_data="product")
    pricing_btn = types.InlineKeyboardButton("💰 Посмотреть цены и тарифы", callback_data="pricing")
    status_btn = types.InlineKeyboardButton("📊 Статус моей подписки", callback_data="status")
    menu_btn = types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
    markup.add(product_btn, pricing_btn, status_btn, menu_btn)
    return markup

def get_product_keyboard():
    """Клавиатура для раздела продукта"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    basic_btn = types.InlineKeyboardButton("🟢 Оформить Базовый (999₽)", callback_data="subscribe_basic")
    premium_btn = types.InlineKeyboardButton("🟡 Оформить Премиум (1999₽)", callback_data="subscribe_premium")
    vip_btn = types.InlineKeyboardButton("🟠 Оформить VIP (3999₽)", callback_data="subscribe_vip")
    back_btn = types.InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="back")
    markup.add(basic_btn, premium_btn, vip_btn, back_btn)
    return markup

def get_pricing_keyboard():
    """Клавиатура для раздела цен с кнопками покупки"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    basic_btn = types.InlineKeyboardButton("🟢 Оформить Базовый (999₽)", callback_data="subscribe_basic")
    premium_btn = types.InlineKeyboardButton("🟡 Оформить Премиум (1999₽)", callback_data="subscribe_premium")
    vip_btn = types.InlineKeyboardButton("🟠 Оформить VIP (3999₽)", callback_data="subscribe_vip")
    back_btn = types.InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="back")
    markup.add(basic_btn, premium_btn, vip_btn, back_btn)
    return markup

def get_subscription_keyboard():
    """Клавиатура выбора тарифов"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    basic_btn = types.InlineKeyboardButton("🟢 Оформить Базовый (999₽)", callback_data="subscribe_basic")
    premium_btn = types.InlineKeyboardButton("🟡 Оформить Премиум (1999₽)", callback_data="subscribe_premium")
    vip_btn = types.InlineKeyboardButton("🟠 Оформить VIP (3999₽)", callback_data="subscribe_vip")
    back_btn = types.InlineKeyboardButton("⬅️ Назад в главное меню", callback_data="back")
    markup.add(basic_btn, premium_btn, vip_btn, back_btn)
    return markup

def get_payment_keyboard(payment_url):
    """Клавиатура для оплаты"""
    markup = types.InlineKeyboardMarkup()
    pay_btn = types.InlineKeyboardButton("💳 Оплатить", url=payment_url)
    back_btn = types.InlineKeyboardButton("⬅️ Назад к тарифам", callback_data="back")
    markup.add(pay_btn, back_btn)
    return markup

def get_success_keyboard():
    """Клавиатура после успешной оплаты"""
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back")
    markup.add(back_btn)
    return markup

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
