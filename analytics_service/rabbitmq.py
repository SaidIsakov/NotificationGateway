import pika
from decouple import config


def connect_rabbitmq():
  host = config('RABBITMQ_HOST')
  port = config('RABBITMQ_PORT')

  credentails = pika.PlainCredentials(username='guest', password='guest')

  parametrs = pika.ConnectionParameters(host=str(host), port=int(port), credentials=credentails)

  connection = pika.BlockingConnection(parameters=parametrs)

  channel = connection.channel()

  return channel, connection
