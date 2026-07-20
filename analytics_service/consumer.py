from django.utils import timezone
from decimal import Decimal
import json
import logging
import os
from rabbitmq import connect_rabbitmq
from django.db.models import F


logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
import django
django.setup()

from apps.analytics.models import OrderEvent, DailyMetrics

def on_massage(channel, method, properties, body):
  try:
    data = json.loads(body)
    event_type = data.get('event')
    order_id = data.get('order_id')
    product_name = data.get('product_name')
    price = Decimal(data.get('price') or '0')
    user_email = data.get('user_email')
    user_telegram_id = data.get('user_telegram_id')

    metrics, created = DailyMetrics.objects.get_or_create(
       date = timezone.now().date(),
       defaults={
          'total_orders': 0,
          'paid_orders': 0,
          'cancelled_orders': 0,
          'total_revenue': 0,
          'conversion_rate': 0
       }
     )

    if event_type == 'order.created':
      order_event = OrderEvent.objects.create(
        event_type='created',
        order_id = order_id,
        product_name=product_name,
        price=price
      )
      logger.info(f"Создан order_event с заказом {order_event.order_id}. product_name: {order_event.product_name}")

      metrics.total_orders = F('total_orders') + 1

      metrics.save()
      metrics.refresh_from_db()


    elif event_type == 'order.paid':
      order_event = OrderEvent.objects.create(
        event_type='paid',
        order_id = order_id,
        product_name=product_name,
        price=price
      )
      metrics.paid_orders = F('paid_orders') + 1
      metrics.total_revenue = F('total_revenue') + price

      metrics.save()
      metrics.refresh_from_db()


    elif event_type == 'order.cancelled':
      order_event = OrderEvent.objects.create(
        event_type='cancelled',
        order_id = order_id,
        product_name=product_name,
        price=price
      )
      metrics.cancelled_orders = F('cancelled_orders') + 1

      metrics.save()
      metrics.refresh_from_db()

    if metrics.total_orders == 0:
      metrics.conversion_rate = Decimal(0)
    else:
      conversion_rate = (metrics.paid_orders / metrics.total_orders) * 100
      metrics.conversion_rate = Decimal(conversion_rate)

    metrics.save()
    channel.basic_ack(delivery_tag=method.delivery_tag)


  except Exception as e:
    logger.error(f"Произошла ошибка: {e}")
    channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
  channel, connection = connect_rabbitmq()

  channel.exchange_declare(exchange='order_events', exchange_type='direct', durable=True)

  channel.queue_declare(queue='analytics_queue', durable=True)

  channel.queue_bind(queue='analytics_queue', exchange='order_events', routing_key='order.created')
  channel.queue_bind(queue='analytics_queue', exchange='order_events', routing_key='order.paid')
  channel.queue_bind(queue='analytics_queue', exchange='order_events', routing_key='order.cancelled')

  channel.basic_consume(queue='analytics_queue', on_message_callback=on_massage)

  channel.start_consuming()

