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
  print("!!! 1. НАЧАЛО ОБРАБОТКИ СООБЩЕНИЯ !!!")
  try:
    data = json.loads(body)
    event_type = data.get('event')
    order_id = data.get('order_id')
    product_name = data.get('product')
    user_email = data.get('user_email')
    user_telegram_id = data.get('user_telegram_id')

    try:

      product_slug = slugify(product_name)
      print(f"!!! 2. Поиск товара по slug: {product_slug} !!!")
      print(f"🔍 ИЩУ ТОВАР ПО НАЗВАНИЮ: '{product_name}' -> slug: '{product_slug}'")
      sys.stdout.flush()
      product = Product.objects.get(slug=product_slug)
      print(f"!!! 3. Товар найден: {product.name}, остаток: {product.stock} !!!")

      if event_type == 'order.paid' and product.stock > 0:
        product.stock -= 1
        product.save()
        print(f"!!! 4a. Товар списан. Остаток: {product.stock} !!!")

      elif event_type == 'order.created' and product.stock == 0:
        logger.warning(f"Товар {product_name} закончился на складе. Отменяем заказ {order_id}")
        send_warehouse_exchange(order_id=order_id, product_name=product_name, user_email=user_email, user_telegram_id=user_telegram_id)
        print("!!! 5. Функция send_warehouse_exchange ПРОПУЩЕНА !!!")


    except Product.DoesNotExist:
      print("!!! 4c. Товар НЕ НАЙДЕН в БД !!!")
      #! Делаем publisher на notification_service с сообщением

    print("!!! 6. ОТПРАВЛЯЕМ ACK В RABBITMQ !!!")
    channel.basic_ack(delivery_tag=method.delivery_tag)
    print("!!! 7. ОБРАБОТКА ПОЛНОСТЬЮ ЗАВЕРШЕНА !!!")

  except Exception as e:
    print(f"!!! 8. КРИТИЧЕСКАЯ ОШИБКА: {e} !!!")
    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

if __name__ == '__main__':
  print("!!! ЗАПУСК CONSUMER-А !!!")
  logger.info('Подключение к RabbitMQ')

  channel, connection = connect_rabbitmq()

  channel.exchange_declare(exchange='order_events', exchange_type='direct', durable=True)

  channel.queue_declare(queue='warehouse_queue', durable=True)

  channel.queue_bind(queue='warehouse_queue', exchange='order_events', routing_key='order.created')
  channel.queue_bind(queue='warehouse_queue', exchange='order_events', routing_key='order.paid')

  channel.basic_consume(queue='warehouse_queue', on_message_callback=on_message)

  print("!!! ОЖИДАНИЕ СООБЩЕНИЙ (нажмите CTRL+C для выхода) !!!")
  channel.start_consuming()

