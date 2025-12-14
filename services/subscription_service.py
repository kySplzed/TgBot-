# services/subscription_service.py - бизнес-логика для управления подписками

from datetime import datetime, timedelta
from typing import Optional
from config import PLANS
from db.database import get_user_subscription, save_subscription, check_expired_subscriptions
from db.models import Subscription

def activate_subscription(user_id: int, plan: str, payment_id: Optional[str] = None) -> Subscription:
    """Активация подписки для пользователя"""

    plan_info = PLANS[plan]

    # Проверяем, есть ли уже активная подписка
    existing_subscription = get_user_subscription(user_id)

    if existing_subscription and existing_subscription.status == 'active':
        # Продлеваем существующую подписку
        end_date = datetime.fromisoformat(existing_subscription.end_date)
        end_date = end_date + timedelta(days=30)  # +30 дней
        start_date = existing_subscription.start_date
    else:
        # Создаем новую подписку
        start_date = datetime.now().isoformat()
        end_date = datetime.now() + timedelta(days=30)

    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        plan_name=plan_info['name'],
        price=plan_info['price'],
        start_date=start_date,
        end_date=end_date.isoformat(),
        status='active',
        auto_renewal=True,
        payment_id=payment_id
    )

    save_subscription(subscription)
    return subscription

def get_user_subscription(user_id: int) -> Optional[Subscription]:
    """Получение информации о подписке пользователя"""
    return get_user_subscription(user_id)

def cancel_subscription(user_id: int) -> bool:
    """Отмена подписки пользователя"""
    subscription = get_user_subscription(user_id)
    if subscription and subscription.status == 'active':
        subscription.status = 'canceled'
        subscription.auto_renewal = False
        save_subscription(subscription)
        return True
    return False

def get_subscription_status_text(subscription: Optional[Subscription]) -> str:
    """Формирование текста статуса подписки"""

    if not subscription:
        return "❌ У вас нет активной подписки"

    status_emoji = {
        'active': '✅',
        'expired': '⏰',
        'canceled': '🚫'
    }

    status_text = f"""
{status_emoji.get(subscription.status, '❓')} **Статус подписки**

**Тариф:** {subscription.plan_name}
**Стоимость:** {subscription.price}₽/месяц
**Статус:** {subscription.status.title()}
**Дата активации:** {subscription.start_date[:10]}
**Дата окончания:** {subscription.end_date[:10]}

**Автопродление:** {'Включено' if subscription.auto_renewal else 'Отключено'}
"""

    if subscription.status == 'active':
        end_date = datetime.fromisoformat(subscription.end_date)
        days_left = (end_date - datetime.now()).days
        status_text += f"\n**Осталось дней:** {days_left}"

    return status_text

def check_expired_subscriptions() -> int:
    """Проверка и обновление истекших подписок. Возвращает количество обновленных подписок."""
    return check_expired_subscriptions()
