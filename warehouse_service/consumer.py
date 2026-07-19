from codecs import lookup
import json
import logging
import os
from django.utils.text import slugify
from publisher import send_warehouse_exchange
import sys


logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
import django
django.setup()

from rabbitmq import connect_rabbitmq
from apps.warehouse.models import Product


def on_message(channel, method, properties, body):
  try:
    data = json.loads(body)
    event_type = data.get('event')
    order_id = data.get('order_id')
    product_name = data.get('product')
    user_email = data.get('user_email')
    user_telegram_id = data.get('user_telegram_id')

    try:
      product_slug = slugify(product_name)
      sys.stdout.flush()
      product = Product.objects.get(slug=product_slug)
      logger.info(f"3. Товар найден: {product.name}, остаток: {product.stock} !!!")

      if event_type == 'order.paid' and product.stock > 0:
        product.stock -= 1
        product.save()

      elif event_type == 'order.created' and product.stock == 0:
        logger.warning(f"Товар {product_name} закончился на складе. Отменяем заказ {order_id}")
        send_warehouse_exchange(order_id=order_id, product_name=product_name, user_email=user_email, user_telegram_id=user_telegram_id)


    except Product.DoesNotExist:
      logger.error('Товар не найден')
      #! Делаем publisher на notification_service с сообщением

    channel.basic_ack(delivery_tag=method.delivery_tag)

  except Exception as e:
    logger.error(f'Ошибка: {e}')
    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == '__main__':
  logger.info('Подключение к RabbitMQ')

  channel, connection = connect_rabbitmq()

  channel.exchange_declare(exchange='order_events', exchange_type='direct', durable=True)

  channel.queue_declare(queue='warehouse_queue', durable=True)

  channel.queue_bind(queue='warehouse_queue', exchange='order_events', routing_key='order.created')
  channel.queue_bind(queue='warehouse_queue', exchange='order_events', routing_key='order.paid')

  channel.basic_consume(queue='warehouse_queue', on_message_callback=on_message)

  channel.start_consuming()

