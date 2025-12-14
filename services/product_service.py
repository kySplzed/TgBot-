# services/product_service.py - бизнес-логика для работы с продуктами

from config import PLANS

def get_available_plans():
    """Получить доступные тарифные планы"""
    return PLANS

def get_plan_info(plan_name):
    """Получить информацию о конкретном плане"""
    return PLANS.get(plan_name)

def validate_plan(plan_name):
    """Проверить существование плана"""
    return plan_name in PLANS

def get_plan_features(plan_name):
    """Получить особенности плана"""
    plan = get_plan_info(plan_name)
    if plan:
        return {
            'name': plan['name'],
            'price': plan['price'],
            'description': plan['description'],
            'duration_days': plan['duration_days']
        }
    return None
