# utils/state_manager.py - менеджер состояний для бота

# Класс для управления состояниями пользователей в диалогах
class StateManager:
    """Менеджер состояний пользователей"""

    def __init__(self):
        self.user_states = {}  # user_id -> state

    def set_state(self, user_id, state):
        """Установить состояние для пользователя"""
        self.user_states[user_id] = state

    def get_state(self, user_id):
        """Получить состояние пользователя"""
        return self.user_states.get(user_id)

    def clear_state(self, user_id):
        """Очистить состояние пользователя"""
        if user_id in self.user_states:
            del self.user_states[user_id]

    def has_state(self, user_id):
        """Проверить, есть ли состояние у пользователя"""
        return user_id in self.user_states

# Глобальный экземпляр менеджера состояний
state_manager = StateManager()

# Вспомогательные функции
def set_user_state(user_id, state):
    """Установить состояние пользователя"""
    state_manager.set_state(user_id, state)

def get_user_state(user_id):
    """Получить состояние пользователя"""
    return state_manager.get_state(user_id)

def clear_user_state(user_id):
    """Очистить состояние пользователя"""
    state_manager.clear_state(user_id)

def has_user_state(user_id):
    """Проверить состояние пользователя"""
    return state_manager.has_state(user_id)
