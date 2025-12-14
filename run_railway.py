#!/usr/bin/env python3
# run_railway.py - Entry point для Railway

import os
import sys
import threading
from webhook import app
from main import main as run_bot
from logger import setup_logging

def start_bot():
    """Запуск бота в отдельном потоке"""
    try:
        run_bot()
    except Exception as e:
        print(f"Bot error: {e}")

def main():
    """Главная функция для Railway"""

    # Настраиваем логирование
    setup_logging()

    print("🚀 Starting Telegram Sales Bot on Railway")

    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()

    print("✅ Bot thread started")

    # Запускаем Flask приложение (адаптивный порт для разных хостингов)
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Starting web server on port {port}")

    # Для production используем production WSGI сервер
    if os.environ.get('ENVIRONMENT') == 'production':
        from waitress import serve
        print("🍽️  Using Waitress WSGI server for production")
        serve(app, host='0.0.0.0', port=port)
    else:
        app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    main()
