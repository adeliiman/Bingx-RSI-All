import pika, sys, os, time, json
import threading
from main import Bingx

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='bingx')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        data = json.loads(body.decode('utf-8').replace("'",'"'))
        Bingx.position = data['symbol']
        Bingx.temp_pos = False


    channel.basic_consume(queue='bingx', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

threading.Thread(target=main).start()
threading.Thread(target=main).start()
