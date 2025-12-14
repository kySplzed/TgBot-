# webhook.py - обработка webhook уведомлений от YooKassa

import json
from flask import Flask, request, jsonify
from services.payment_service import process_webhook_payment_succeeded, process_webhook_payment_failed
from utils.logger import get_logger
from config import WEBHOOK_HOST, WEBHOOK_PORT, DEBUG

logger = get_logger(__name__)

app = Flask(__name__)

@app.route('/yookassa/webhook', methods=['POST'])
def yookassa_webhook():
    """Обработка webhook уведомлений от YooKassa"""

    try:
        # Получаем данные от YooKassa
        data = request.get_json()

        if not data:
            logger.warning("No data received in webhook")
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Проверяем тип события
        event = data.get('event')
        logger.info(f"Received webhook event: {event}")

        if event == 'payment.succeeded':
            # Платеж успешно завершен
            if process_webhook_payment_succeeded(data):
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
