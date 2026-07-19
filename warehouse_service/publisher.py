import json
import logging
from rabbitmq import connect_rabbitmq
import pika

logger = logging.getLogger(__name__)

def send_warehouse_exchange(order_id: int, product_name: str, user_email, user_telegram_id):
  try:
    channel, connection = connect_rabbitmq()

    channel.exchange_declare(exchange='order_events', exchange_type='direct', durable=True)

    message = {
    'event': 'order.cancelled',
    'order_id': order_id,
    'product_name': str(product_name),
    'user_email': user_email,
    'user_telegram_id': user_telegram_id
    }

    channel.basic_publish(
    exchange='order_events',
    routing_key='order.cancelled',
    body=json.dumps(message),
    properties=pika.BasicProperties(
      delivery_mode=2
      )
    )
    logger.info(f"Отправлено сообщение: {message}")
  finally:
    try:
      connection.close()
    except:
      pass
