# webhook.py - обработка webhook уведомлений от YooKassa

import json
from datetime import datetime
from flask import Flask, request, jsonify
from services.payment_service import process_webhook_payment_succeeded, process_webhook_payment_failed, process_payment_success
from utils.logger import get_logger
from config import WEBHOOK_HOST, WEBHOOK_PORT, DEBUG, API_TOKEN

logger = get_logger(__name__)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Главная страница сервера с информацией о доступных эндпоинтах"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Bot Webhook Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; }}
            .endpoint {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }}
            .method {{ font-weight: bold; color: #e74c3c; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Telegram Bot Webhook Server</h1>
            <p>Сервер для обработки webhook уведомлений от YooKassa</p>

            <div class="warning">
                <strong>⚠️ Внимание:</strong> Это development сервер. В продакшене используйте WSGI сервер (gunicorn, uwsgi).
            </div>

            <h2>📋 Доступные эндпоинты:</h2>

            <div class="endpoint">
                <span class="method">GET</span> <code>/</code><br>
                <strong>Главная страница</strong> - эта страница
            </div>

            <div class="endpoint">
                <span class="method">GET</span> <code>/health</code><br>
                <strong>Health check</strong> - проверка работоспособности сервера
            </div>

            <div class="endpoint">
                <span class="method">POST</span> <code>/yookassa/webhook</code><br>
                <strong>Webhook YooKassa</strong> - обработка платежных уведомлений
            </div>

            <div class="endpoint">
                <span class="method">GET</span> <code>/test-payment/<user_id>/<plan></code><br>
                <strong>Тест платежа</strong> - имитация успешного платежа (для тестирования)
            </div>

            <h2>🧪 Тестирование:</h2>
            <p>Попробуйте:</p>
            <ul>
                <li><a href="/health">Проверить здоровье сервера</a></li>
                <li><a href="/test-payment/123/basic">Тестовый платеж</a></li>
            </ul>

            <p><strong>Статус:</strong> Сервер работает ✅</p>
            <p><strong>Время запуска:</strong> {current_time}</p>
        </div>
    </body>
    </html>
    '''

@app.route('/yookassa/webhook', methods=['GET', 'POST', 'PUT'])
def yookassa_webhook():
    """Обработка webhook уведомлений от YooKassa"""

    try:
        logger.info(f"Webhook received: Method={request.method}, URL={request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Content-Type: {request.headers.get('Content-Type')}")
        logger.info(f"Content-Length: {request.headers.get('Content-Length')}")

        # Получаем данные от YooKassa - всегда пробуем парсить как JSON
        try:
            # Сначала пробуем стандартный способ
            data = request.get_json()
        except Exception:
            try:
                # Если не получилось, пробуем force parsing
                data = request.get_json(force=True)
            except Exception:
                # Если и force не помог, получаем raw data
                raw_data = request.get_data(as_text=True)
                logger.info(f"Raw webhook data (length: {len(raw_data)}): {raw_data[:500]}...")
                try:
                    # Пробуем распарсить как JSON
                    data = json.loads(raw_data)
                except Exception as e:
                    logger.error(f"Cannot parse webhook data as JSON: {e}")
                    logger.error(f"Raw data: {raw_data}")
                    return jsonify({'status': 'error', 'message': 'Cannot parse data'}), 400

        if not data:
            logger.warning("No data received in webhook")
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        logger.info(f"Webhook data: {data}")

        # Проверяем тип события
        event = data.get('event')
        logger.info(f"Received webhook event: {event}")

        if event == 'payment.succeeded':
            # Платеж успешно завершен
            if process_webhook_payment_succeeded(data):
                # Создаем временный экземпляр бота для отправки уведомления
                try:
                    import telebot
                    temp_bot = telebot.TeleBot(API_TOKEN)

                    # Получаем информацию о платеже из metadata
                    metadata = data.get('object', {}).get('metadata', {})
                    payment_id = metadata.get('payment_id')

                    if payment_id:
                        # Отправляем уведомление пользователю
                        process_payment_success(temp_bot, payment_id)
                        logger.info("Payment success notification sent to user")
                    else:
                        logger.warning("No payment_id in webhook metadata for user notification")

                except Exception as e:
                    logger.error(f"Error sending payment success notification: {e}")

                logger.info("Payment succeeded webhook processed successfully")
                return jsonify({'status': 'success'}), 200
            else:
                logger.error("Failed to process payment succeeded webhook")
                return jsonify({'status': 'error', 'message': 'Processing failed'}), 500

        elif event == 'payment.canceled':
            # Платеж отменен
            payment_data = data.get('object', {})
            logger.info(f"Payment {payment_data.get('id')} was canceled")
            # Можно добавить дополнительную обработку отмены платежа
            return jsonify({'status': 'success'}), 200

        elif event == 'payment.failed':
            # Платеж не удался
            if process_webhook_payment_failed(data):
                logger.info("Payment failed webhook processed successfully")
                return jsonify({'status': 'success'}), 200
            else:
                logger.error("Failed to process payment failed webhook")
                return jsonify({'status': 'error', 'message': 'Processing failed'}), 500

        elif event == 'payment.waiting_for_capture':
            # Платеж ожидает подтверждения
            payment_data = data.get('object', {})
            logger.info(f"Payment {payment_data.get('id')} is waiting for capture")
            return jsonify({'status': 'success'}), 200

        logger.warning(f"Unhandled webhook event: {event}")
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервера"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/test-payment/<user_id>/<plan>', methods=['GET'])
def test_payment(user_id, plan):
    """Тестовый эндпоинт для имитации успешного платежа"""

    # Имитируем webhook уведомление
    mock_webhook_data = {
        "event": "payment.succeeded",
        "object": {
            "id": f"test_payment_{user_id}_{plan}",
            "status": "succeeded",
            "metadata": {
                "payment_id": f"test_{user_id}_{plan}",
                "user_id": user_id,
                "plan": plan
            }
        }
    }

    # Обрабатываем как обычный webhook
    if process_webhook_payment_succeeded(mock_webhook_data):
        return jsonify({
            'status': 'success',
            'message': f'Подписка {plan} активирована для пользователя {user_id}',
            'user_id': user_id,
            'plan': plan
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Ошибка активации подписки'
        }), 500

if __name__ == '__main__':
    # В продакшене используйте WSGI сервер (gunicorn, uwsgi)
    logger.info(f"Starting webhook server on port {WEBHOOK_PORT}")
    app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=DEBUG)
