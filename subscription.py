# subscription.py - управление подписками пользователей

import json
from datetime import datetime, timedelta
from config import PLANS

# В реальном приложении используйте базу данных
SUBSCRIPTIONS_FILE = 'subscriptions.json'

def load_subscriptions():
    """Загрузка подписок из файла"""
    try:
        with open(SUBSCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_subscriptions(subscriptions):
    """Сохранение подписок в файл"""
    with open(SUBSCRIPTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(subscriptions, f, ensure_ascii=False, indent=2, default=str)

def activate_subscription(user_id, plan):
    """Активация подписки для пользователя"""

    subscriptions = load_subscriptions()

    # Проверяем, есть ли уже активная подписка
    if str(user_id) in subscriptions:
        current_sub = subscriptions[str(user_id)]
        if current_sub['status'] == 'active' and current_sub['end_date'] > datetime.now().isoformat():
            # Продлеваем существующую подписку
            end_date = datetime.fromisoformat(current_sub['end_date'])
            end_date = end_date + timedelta(days=30)  # +30 дней
        else:
            # Создаем новую подписку
            end_date = datetime.now() + timedelta(days=30)
    else:
        # Создаем новую подписку
        end_date = datetime.now() + timedelta(days=30)

    subscription_data = {
        'user_id': user_id,
        'plan': plan,
        'plan_name': PLANS[plan]['name'],
        'price': PLANS[plan]['price'],
        'start_date': datetime.now().isoformat(),
        'end_date': end_date.isoformat(),
        'status': 'active',
        'auto_renewal': True
    }

    subscriptions[str(user_id)] = subscription_data
    save_subscriptions(subscriptions)

    return subscription_data

def get_user_subscription(user_id):
    """Получение информации о подписке пользователя"""

    subscriptions = load_subscriptions()

    if str(user_id) in subscriptions:
        sub = subscriptions[str(user_id)]

        # Проверяем, не истекла ли подписка
        if sub['status'] == 'active':
            end_date = datetime.fromisoformat(sub['end_date'])
            if end_date < datetime.now():
                sub['status'] = 'expired'
                save_subscriptions(subscriptions)

        return sub

    return None

def cancel_subscription(user_id):
    """Отмена подписки пользователя"""

    subscriptions = load_subscriptions()

    if str(user_id) in subscriptions:
        subscriptions[str(user_id)]['status'] = 'canceled'
        subscriptions[str(user_id)]['auto_renewal'] = False
        save_subscriptions(subscriptions)
        return True

    return False

def get_subscription_status_text(subscription):
    """Формирование текста статуса подписки"""

    if not subscription:
        return "❌ У вас нет активной подписки"

    status_emoji = {
        'active': '✅',
        'expired': '⏰',
        'canceled': '🚫'
    }

    status_text = f"""
{status_emoji.get(subscription['status'], '❓')} **Статус подписки**

**Тариф:** {subscription['plan_name']}
**Стоимость:** {subscription['price']}₽/месяц
**Статус:** {subscription['status'].title()}
**Дата активации:** {subscription['start_date'][:10]}
**Дата окончания:** {subscription['end_date'][:10]}

**Автопродление:** {'Включено' if subscription.get('auto_renewal', False) else 'Отключено'}
"""

    if subscription['status'] == 'active':
        end_date = datetime.fromisoformat(subscription['end_date'])
        days_left = (end_date - datetime.now()).days
        status_text += f"\n**Осталось дней:** {days_left}"

    return status_text

def check_expired_subscriptions():
    """Проверка и обновление истекших подписок (для cron job)"""

    subscriptions = load_subscriptions()
    updated = False

    for user_id, sub in subscriptions.items():
        if sub['status'] == 'active':
            end_date = datetime.fromisoformat(sub['end_date'])
            if end_date < datetime.now():
                sub['status'] = 'expired'
                updated = True

    if updated:
        save_subscriptions(subscriptions)

    return updated
