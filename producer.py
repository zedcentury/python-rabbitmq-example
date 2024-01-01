import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='salom')

channel.basic_publish(exchange='',
                      routing_key='salom',
                      body=b'Salom dunyo!')

connection.close()
