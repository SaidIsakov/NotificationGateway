import logging
import pika
import json
from rabbitmq import connect_rabbitmq, declare_orders_exchange
import logging


logger = logging.getLogger(__name__)

def send_orders_exchange(order, event_type: str):
  channel, connection = connect_rabbitmq()

  try:
    declare_orders_exchange(channel)

    message = {
        'event': event_type,
        'order_id': str(order.id),
        'user_email': order.user_email,
        'user_telegram_id': order.user_telegram_id,
        'product_name': order.product_name,
        'price': str(order.price),
    }

    channel.basic_publish(
        exchange='order_events',
        routing_key=event_type,
        body=json.dumps(message),
        properties=pika.BasicProperties(
          delivery_mode=2,
        )
    )
    logging.info(f"Отправлено: {message}")
  finally:
    connection.close()
