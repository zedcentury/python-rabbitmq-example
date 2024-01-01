# Pythonda RabbitMQ bilan ishlash

![](https://i.imgur.com/rUsOdLU.png)

### RabbitMQ nima?

RabbitMQ - xabarlar menjeri bo'lib, u Erlang dasturlash tilida yozilgan. U bir nechta xizmat(servis)lar o'rtasida
ma'lumotlarni yuborish(xabarlar) uchun mo'ljallangan: bitta xizmat navbatga xabar joylaydi, boshqa xizmat esa o'sha
xabarni qabul qiladi.

### RabbitMQni o'rnatish va ishga tushirish

Terminalda o'rnatish:

```bash
brew install rabbitmq
```

RabbitMQni ishga tushirish:

```bash
brew services start rabbitmq
```

RabbitMQ http://localhost:15672/ manzilida ishga tushadi. Istalgan brauzer orqali shu manzilga kirilganda sizdan
`username` va `password` so'raladi.

![Login Page](https://i.imgur.com/rVNy4Ch.png)

Standart holatda

```text
username: guest
password: guest
```

bo'ladi.

### RabbitMQ bilan ishlashni boshlash

RabbitMQ plaginlari bilan ishlash uchun `rabbitmq-plugins` buyrug'idan foydalanamiz. Plaginlar ro'yxatini ko'rish uchun
quyidagi komandani yozamiz:

```bash
rabbitmq-plugins list
```

Terminalda turli xil plaginlar ro'yxatini ko'rinishimiz mumkin va biz ulardan RabbitMQni ishlatishda foydalanamiz.

Agar `rabbitmq-plugins` buyrug'i topilmadi degan xato chiqsa, `~/.bash_profile` ichida RabbitMQning manzilini ko'rsatib
qo'yish kerak:

```text
export PATH=$PATH:/usr/local/opt/rabbitmq/sbin
```

RabbitMQning 4 ta muhim tushunchasi bor:

* producer - mijoz, u xabarlarni yuboradi
* queue - xabarlar navbati
* consumer - mijoz, u navbatdan xabarlarni oladi
* exchange - u producerdan xabarlarni oladi, xabar turiga qarab uni kerakli navbatga yuboradi

### Python orqali RabbitMQ bilan ishlash

Pythonda yangi proyekt yaratib olamiz.

RabbitMQ bilan ishlash uchun AMQP (Advanced Message Queuing Protocol) kerak bo'ladi. Pythonda u bilan `pika` kutubxonasi
yordamida ishlash mumkin.

`pika` kutubxonasini o'rnatish

```bash
pip install pika
```

Ana endi proyekt ichida `producer.py` faylini yaratib olamiz va uning ichiga quyidagi kodni yozamiz:

```python
import pika

# Localhostda ishlayotgan RabbitMQ serveriga ulanadi
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

# RabbitMQ bilan aloqa o'rnatiladigan kanal yaratadi
channel = connection.channel()

# 'salom' deb nomlangan navbat mavjudligini tekshiradi, agar mavjud bo'lmasa yaratadi
channel.queue_declare(queue='salom')

# 'salom' navbatiga 'Salom dunyo!' xabarini qo'shadi
channel.basic_publish(exchange='',
                      routing_key='salom',
                      body=b'Salom dunyo!')

# RabbitMQ bilan aloqa uziladi
connection.close()
```

Kodni ishga tushiramiz:

```bash
python producer.py
```

Endi xabar navbatga qo'shilganini tekshirib ko'rinishimiz kerak.

Buning uchun `rabbitmqadmin` buyrug'idan foydalanamiz. `rabbitmqadmin` buyrug'idan foydalanish
uchun `rabbitmq_management` plagini yoqilgan bo'lishi kerak.

Yoqilgan plaginlar ro'yxatini quyidagi komanda orqali ko'rish mumkin:

```bash
rabbitmq-plugins list -E
```

Agar ro'yxatda `rabbitmq_management` plagini bo'lmasa, uni yoqish uchun quyidagi komandadan foydalanamiz:

```bash
rabbitmq-plugins enable rabbitmq_management
```

Ana endi xabar `salom` navbatiga qo'shilganini tekshirib ko'rishimiz mumkin:

```bash
rabbitmqadmin get queue='salom'
```

Natija

```text
+-------------+----------+---------------+--------------+---------------+------------------+------------+-------------+
| routing_key | exchange | message_count |   payload    | payload_bytes | payload_encoding | properties | redelivered |
+-------------+----------+---------------+--------------+---------------+------------------+------------+-------------+
| salom       |          | 0             | Salom dunyo! | 12            | string           |            | False       |
+-------------+----------+---------------+--------------+---------------+------------------+------------+-------------+
```

Barcha navbatlar ro'yxatini ko'rish uchun esa:

```bash
rabbitmqctl list_queues
```

Natija

```text
Timeout: 60.0 seconds ...
Listing queues for vhost / ...
name    messages
salom   1
```

Ko'rinib turibdiki, `salom` navbatida 1 dona xabar mavjud.

Navbatdan xabarni o'qib olish uchun proyektimizda consumer.py faylini yaratamiz va uning ichiga ushbu kodni yozamiz:

```python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

channel = connection.channel()

channel.queue_declare(queue='salom')


# Xabar kelganda ishga tushadigan funksiya e'lon qilingan
def callback(ch, method, properties, body):
    print("[x] Qabul qilindi %r" % body)


# 'salom' navbatini tinglaydi va kelgan xabarlarni callback funksiyasiga yuboradi
channel.basic_consume(queue='salom', on_message_callback=callback, auto_ack=True)

print('[*] Xabarlar kutilmoqda. Chiqish uchun CTRL+C tugmalarini bosing')

# Xabarlarni tinglash ishga tushadi
channel.start_consuming()
```

Faylni ishga tushiramiz:

```bash
python consumer.py
```

Natija:

```text
[*] Xabarlar kutilmoqda. Chiqish uchun CTRL+C tugmalarini bosing
[x] Qabul qilindi b'Salom dunyo!'
```

Chiqish uchun CTRL+C tugmalarini bosamiz.

Navbatlar ro'yxatini qaytadan tekshiramiz.

```bash
rabbitmqctl list_queues
```

Natija

```text
Timeout: 60.0 seconds ...
Listing queues for vhost / ...
name    messages
salom   0
```

Ana endi `salom` navbatida xabarlar mavjud emasligini ko'rishimiz mumkin.
