# main.py - главный файл бота

import sys
import telebot
from config import API_TOKEN, DEBUG, ENVIRONMENT, WEBHOOK_HOST, WEBHOOK_PORT, WEBHOOK_PATH
from handlers import setup_handlers
from utils.logger import setup_logging, get_logger
from db.database import init_database, check_expired_subscriptions

def main():
    """Главная функция приложения"""

    # Инициализируем базу данных
    init_database()

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

        if ENVIRONMENT == 'production':
            # Production mode - используем webhook
            logger.info("🎯 Запуск в режиме webhook для production")

            # Устанавливаем webhook
            webhook_url = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
            bot.set_webhook(url=webhook_url)
            logger.info(f"✅ Webhook установлен: {webhook_url}")

            # Запускаем Flask приложение для обработки webhook
            from webhook import app
            app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=DEBUG)

        else:
            # Development mode - используем polling
            logger.info("🎯 Запуск в режиме polling для development")
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
