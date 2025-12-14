# main.py - главный файл бота

import sys
import telebot
from config import API_TOKEN, DEBUG, ENVIRONMENT
from handlers import setup_handlers
from logger import setup_logging, get_logger

def main():
    """Главная функция приложения"""

    # Настраиваем логирование
    setup_logging()
    logger = get_logger(__name__)

    try:
        # Проверяем токен
        if not API_TOKEN or API_TOKEN == 'ВАШ_НАСТОЯЩИЙ_ТОКЕН_БОТА':
            logger.error("❌ TELEGRAM_BOT_TOKEN не настроен!")
            logger.error("Установите токен в переменной окружения TELEGRAM_BOT_TOKEN")
            sys.exit(1)

        logger.info("🚀 Запуск Telegram Sales Bot")
        logger.info(f"🌍 Среда: {ENVIRONMENT}")
        logger.info(f"🐛 Режим отладки: {DEBUG}")

        # Создаем бота
        bot = telebot.TeleBot(API_TOKEN)
        logger.info("✅ Бот инициализирован")

        # Настраиваем обработчики
        setup_handlers(bot)
        logger.info("✅ Обработчики настроены")

        logger.info("🎯 Бот запущен и готов к работе!")

        # Запускаем бота
        bot.polling(none_stop=True, interval=1, timeout=30)

    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
