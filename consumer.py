import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

channel = connection.channel()

channel.queue_declare(queue='salom')


def callback(ch, method, properties, body):
    print("[x] Qabul qilindi %r" % body)


channel.basic_consume(queue='salom', on_message_callback=callback, auto_ack=True)

print('[*] Xabarlar kutilmoqda. Chiqish uchun CTRL+C tugmalarini bosing')

channel.start_consuming()
