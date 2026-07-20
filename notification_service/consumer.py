import json
from venv import logger
from rabbitmq import connect_rabbitmq
import django
import os


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

from apps.notifications.tasks import send_notification_task
from apps.notifications.models import Notification

def on_message(channel, method, properties, body):
  try:
    data = json.loads(body)
    event_type = data.get('event')
    print(f" [x] Получено: {data}")

    if data.get('user_telegram_id'):
      channel_type = 'TELEGRAM'
      recipient = data['user_telegram_id']
    else:
      channel_type = 'EMAIL'
      recipient = data['user_email']

    if event_type == 'order.paid':
      subject = f'Заказ {data["order_id"]} оплачен!'
      text = f'Спасибо! Мы уже начали собирать ваш {data["product_name"]}.'
    elif event_type == 'order.cancelled':
      subject = f"Заказ {data['order_id']} отменен"
      text = f"Извините, но на складе закончился товар: {data['product_name']}"
    else:
      print(f" [!] Неизвестное событие: {event_type}")
      channel.basic_ack(delivery_tag=method.delivery_tag)
      return
    notification = Notification.objects.create(
        channel=channel_type,
        recipient=recipient,
        payload={
          'subject': subject,
          'text': text
        },
        status='PENDING'
    )

    send_notification_task.delay(str(notification.id))

    channel.basic_ack(delivery_tag=method.delivery_tag)
  except Exception as e:
    print(f"[!] Ошибка обработки: {e}")


if __name__ == '__main__':
  print("Подключение к RabbitMQ...")
  channel, connection = connect_rabbitmq()

  channel.exchange_declare(exchange='order_events', exchange_type='direct', durable=True)
  channel.queue_declare(queue='notification_queue', durable=True)

  channel.queue_bind(queue='notification_queue', exchange='order_events', routing_key='order.created')
  channel.queue_bind(queue='notification_queue', exchange='order_events', routing_key='order.paid')
  channel.queue_bind(queue='notification_queue', exchange='order_events', routing_key='order.cancelled')

  print(" [*] Слушаю очередь... Нажми CTRL+C для выхода")

  channel.basic_consume(queue='notification_queue', on_message_callback=on_message)

  channel.start_consuming()
