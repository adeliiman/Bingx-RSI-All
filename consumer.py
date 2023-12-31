import pika, sys, os, time, json
import threading
from main import Bingx, api
from utils import update_all_klines
from setLogger import get_logger


logger = get_logger(__name__)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='bingx')

    def callback(ch, method, properties, body):
        try:
            print(f" [x] Received {body}")
            data = json.loads(body.decode('utf-8').replace("'",'"'))
            Bingx.position = data['symbol']
            #
            symbol = data['symbol']
            side = data['side']
            positionSide = data['positionSide']
            price = data['price']
            margin = data['margin']
            qty = margin / price
            rsi = data['rsi']
            time_ = data['time_']
            rsi_level = data['rsi_level']
            leverage = data['leverage']
            margin_mode = data['margin_mode']
            TP = data['TP']
            SL = data['SL']

            from main import placeOrder
            placeOrder(symbol=symbol, side=side, 
                    positionSide=positionSide, 
                    price=price, margin=margin,
                    qty=qty, rsi=rsi, time_=time_, rsi_level=rsi_level,
					leverage=leverage, margin_mode=margin_mode,
					TP=TP, SL=SL
					)
        except Exception as e:
            logger.exception(f"{e}")

    channel.basic_consume(queue='bingx', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

threading.Thread(target=main).start()
threading.Thread(target=main).start()



# def update_klines():
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
#     channel = connection.channel()

#     channel.queue_declare(queue='update-klines')

#     def callback(ch, method, properties, body):
#         print(f" [x] Received {body}")
        
#         update_all_klines(symbols=Bingx.symbols)


#     channel.basic_consume(queue='update-klines', on_message_callback=callback, auto_ack=True)

#     print(' [*] Waiting for update request. To exit press CTRL+C')
#     channel.start_consuming()

# threading.Thread(target=update_klines).start()