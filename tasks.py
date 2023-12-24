import pika, time



def sender(body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='bingx')

    channel.basic_publish(exchange='', routing_key='bingx', body=body)
    print(" [x] Sent 'Hello World!'")

    connection.close()