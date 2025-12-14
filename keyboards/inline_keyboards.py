# keyboards/inline_keyboards.py - Inline клавиатуры бота

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

def get_status_keyboard():
    """Клавиатура для статуса подписки"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    delete_btn = types.InlineKeyboardButton("🗑️ Удалить подписку", callback_data="delete_subscription")
    back_btn = types.InlineKeyboardButton("🏠 В главное меню", callback_data="back")
    markup.add(delete_btn, back_btn)
    return markup

def get_delete_confirmation_keyboard():
    """Клавиатура подтверждения удаления подписки"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    confirm_btn = types.InlineKeyboardButton("✅ Подтверждаю удаление", callback_data="confirm_delete")
    cancel_btn = types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_delete")
    markup.add(confirm_btn, cancel_btn)
    return markup
