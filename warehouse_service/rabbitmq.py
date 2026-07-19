import pika
from decouple import config

def connect_rabbitmq():
  host: str = str(config('RABBITMQ_HOST'))
  port: int = int(config('RABBITMQ_PORT'))
  credentials = pika.PlainCredentials('guest', 'guest')
  parameters = pika.ConnectionParameters(
      host=host,
      port=port,
      credentials=credentials
  )

  connection = pika.BlockingConnection(parameters=parameters)

  channel = connection.channel()

  return channel, connection
