import pika
from dotenv import load_dotenv
import threading
import json,time,os,logging

# Setting Main formatter
main_formatter=logging.Formatter("[%(asctime)s]:[%(module)s] %(levelname)-8s | %(message)s",datefmt="%Y-%m-%d %H:%M:%S")

# settings logging
handler = logging.StreamHandler()
handler.setFormatter(main_formatter)
handler.setLevel(logging.INFO)
main_logger = logging.getLogger("main")
main_logger.addHandler(handler)
main_logger.setLevel(logging.INFO)


# use rabbitmq in docker
RABBIT_URL = "amqp://localhost:5672/"
# exchange name -> add exchange name in rabbitmq management page
EXCHANGE = "TEST_EXCHANGE"
        
    


class ConsumerThread(threading.Thread):
    # if you produce data to rabbitmq queue name with test1, you can get data from this thread
    # check with rabbitmq management page
    
    def __init__(self, thread_number):        
        # initialize thread class        
        super().__init__()
        # set daemon 
        # if you want to stop thread when main thread is stopped, you can set daemon True
        self.daemon = True
                        
        self.thread_number = thread_number
        # for rabbitmq queue name each thread subscriber
        self.queue_name = thread_number+"_q"
        # add blocking connection for rabbitmq
        self.connection = pika.BlockingConnection(
            # rabbitmq parameters
            pika.URLParameters(RABBIT_URL)
        )
        # add channel for rabbitmq
        self.channel = self.connection.channel()
        # add channel queue for rabbitmq
        self.channel.queue_declare(queue=self.queue_name,auto_delete=False)
        # add channel exchange for rabbitmq
        self.channel.queue_bind(exchange=EXCHANGE, queue=self.queue_name, routing_key=thread_number)
        
        # callback function        
        self.consumer = self.channel.basic_consume(
            queue=self.queue_name ,on_message_callback=self.callback, auto_ack=True
        )
        
        
    def callback(self, channel, method, properties, body):
        # actually callback function
        main_logger.info(f"[{self.thread_number}] : callback started")
        try:
            # get body data 
            body = json.loads(body)   
            time.sleep(5)      
            main_logger.info(f"[{self.thread_number}] : sleep 5") 
        except json.JSONDecodeError:
            main_logger.error(f"[{self.thread_number}] : json decode error")
            

    def run(self):               
        self.channel.start_consuming()
        # print consumer thread start
        main_logger.info(f"[{self.thread_number}] : start subcriber")
    
if __name__ == "__main__":
    # consumer threads list 
    consumers = []
    consumers_count = 6
    for i in range(1,consumers_count+1):    
        # generate consumer thread        
        consumers.append(ConsumerThread("test"+str(i)))
    
    for consumer in consumers:        
        # start consumer threads
        consumer.start() 
        main_logger.info("Start consumer Thread : {}".format(consumer.thread_number))
        
    
    runtime = 0
    while True:
        # while for main thread
        main_logger.info("Main Thread is running...{}".format(runtime))
        # sleep 1 second
        time.sleep(1)
        # runtime + 1
        runtime += 1