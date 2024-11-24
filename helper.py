import pika
from threading import Thread

# Establish a connection to RabbitMQ server
def send(message='Hello, World!', queue_name='hello'):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Declare a queue
    channel.queue_declare(queue=queue_name)

    # Send a message
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(" [x] Sent", message)

    # Close the connection
    connection.close()

