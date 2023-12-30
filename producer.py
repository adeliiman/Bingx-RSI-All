import pika, time



def publish(body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='bingx')

    channel.basic_publish(exchange='', routing_key='bingx', body=body)
    print(" [x] Sent 'Hello World!'")

    connection.close()


def update_klines():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='update-klines')

    channel.basic_publish(exchange='', routing_key='update-klines', body="update klines.")
    print(" [x] update klines")

    connection.close()