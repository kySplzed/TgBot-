# webhook.py - обработка webhook уведомлений от YooKassa

import json
from flask import Flask, request, jsonify
from payments import process_payment_success, check_payment_status
from subscription import activate_subscription
from logger import get_logger
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
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Проверяем тип события
        event = data.get('event')

        if event == 'payment.succeeded':
            # Платеж успешно завершен
            payment = data.get('object', {})

            # Извлекаем метаданные
            metadata = payment.get('metadata', {})
            user_id = metadata.get('user_id')
            plan = metadata.get('plan')
            payment_id = payment.get('id')

            if user_id and plan:
                # Активируем подписку
                activate_subscription(int(user_id), plan)

                # Имитируем callback объект для вызова функции обработки
                class MockCall:
                    def __init__(self, user_id, payment_id, plan):
                        self.from_user = type('User', (), {'id': int(user_id)})()
                        self.message = type('Message', (), {
                            'chat': type('Chat', (), {'id': int(user_id)})(),
                            'message_id': 1  # Заглушка
                        })()
                        self.id = f"webhook_{payment_id}"

                mock_call = MockCall(user_id, payment_id, plan)

                # Обрабатываем успешный платеж (имитируем объект бота)
                import telebot
                from config import API_TOKEN

                # Создаем временный экземпляр бота для отправки сообщений
                temp_bot = telebot.TeleBot(API_TOKEN)
                process_payment_success(temp_bot, payment_id)

                print(f"Payment {payment_id} processed successfully for user {user_id}, plan {plan}")
                print(f"Subscription activated for user {user_id}")

                return jsonify({'status': 'success'}), 200
            else:
                print(f"Missing metadata in payment {payment_id}")
                return jsonify({'status': 'error', 'message': 'Missing metadata'}), 400

        elif event == 'payment.canceled':
            # Платеж отменен
            payment = data.get('object', {})
            payment_id = payment.get('id')
            print(f"Payment {payment_id} was canceled")

        elif event == 'payment.waiting_for_capture':
            # Платеж ожидает подтверждения
            payment = data.get('object', {})
            payment_id = payment.get('id')
            print(f"Payment {payment_id} is waiting for capture")

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Webhook processing error: {e}")
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
                "user_id": user_id,
                "plan": plan
            }
        }
    }

    # Обрабатываем как обычный webhook
    result = yookassa_webhook_internal(mock_webhook_data)

    if result:
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

def yookassa_webhook_internal(data):
    """Внутренняя функция обработки webhook (для тестирования)"""
    try:
        event = data.get('event')

        if event == 'payment.succeeded':
            payment = data.get('object', {})
            metadata = payment.get('metadata', {})
            user_id = metadata.get('user_id')
            plan = metadata.get('plan')

            if user_id and plan:
                # Активируем подписку
                from subscription import activate_subscription
                activate_subscription(int(user_id), plan)

                # Имитируем callback объект
                class MockCall:
                    def __init__(self, user_id, payment_id, plan):
                        self.from_user = type('User', (), {'id': int(user_id)})()
                        self.message = type('Message', (), {
                            'chat': type('Chat', (), {'id': int(user_id)})(),
                            'message_id': 1
                        })()
                        self.id = f"webhook_{payment_id}"

                # Обрабатываем успешный платеж (имитируем объект бота)
                import telebot
                from config import API_TOKEN
                from payments import process_payment_success

                # Создаем временный экземпляр бота для отправки сообщений
                temp_bot = telebot.TeleBot(API_TOKEN)
                process_payment_success(temp_bot, payment.get('id', 'test_payment'))

                print(f"Test payment processed for user {user_id}, plan {plan}")
                return True

        return False

    except Exception as e:
        print(f"Test webhook processing error: {e}")
        return False

if __name__ == '__main__':
    # В продакшене используйте WSGI сервер (gunicorn, uwsgi)
    app.run(host='0.0.0.0', port=5000, debug=True)
