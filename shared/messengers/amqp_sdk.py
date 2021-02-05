import pika
import logging

from shared.messengers.messenger import Messenger, MessengerSetting, MessageConsumerSetting


class DundaaAMQPSDKException(Exception): pass

def default_callback(ch, method, properties, body):
    logger = logging.getLogger(__name__)
    logger.info(" [x] %r:%r" % (method.routing_key, body))

class DundaaAMQPSDK(Messenger):
    """
    SDK to handle connection to rabbitAMQP
    """
    def __init__(self, amqp_url=None, amqp_host=None, logger=None):
        if amqp_host is None and amqp_url is None:
            raise RuntimeError("Could not initalise SDK. set either amqp_url or amqp_host")
        self._channel = None
        self._connection = None
        self.amqp_url = amqp_url
        self.amqp_host =amqp_host
        if logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        else:
            self._logger = logger

        self.__connection_established = False

    def _connect(self):
        if self.amqp_url is not None:
            self._connection = pika.BlockingConnection(
                pika.connection.URLParameters(self.amqp_url)
            )
        else:
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.amqp_host)
            )
        self._channel = self._connection.channel()
        self.__connection_established = True

    def publish(self, routing_key: str, data: str, exchange='', exchange_type='direct'):
        self._connect()

        try:
            if exchange_type == 'direct':
                self._publish_direct(exchange=exchange, routing_key=routing_key, data=data)
            else:
                raise DundaaAMQPSDKException("Exchange type not supported!")
        
        except DundaaAMQPSDKException as exc:
            self._logger.error("Could not publish due to exception %s", str(exc))
        
        except Exception as exc:
            self._logger.error("Unknown exception occured %s", str(exc))
        
        finally:
            self._close()
        
    def _publish_direct(self, exchange: str, routing_key: str, data: str):
        self._channel.exchange_declare(exchange=exchange, exchange_type='direct')
        self._channel.basic_publish(
            exchange=exchange, routing_key=routing_key, body=data
        )
        self._logger.info("message published")
    
    def _close(self):
        self._connection.close()



    def __consume(self, exchange: str, routing_keys: [str], exchange_type='direct', callback=None):
        if self.__connection_established is False:
            self._connect()

        self._channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)

        result = self._channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        for key in routing_keys:
            self._channel.queue_bind(
                exchange=exchange, queue=queue_name, routing_key=key)

        self._logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        if callback is None:
            callback = default_callback

        self._channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)

        self._channel.start_consuming()

    def consume_messages(self, consumer_settings: MessageConsumerSetting, callback=None):
        return self.__consume(
            exchange=consumer_settings.service_name,
            routing_keys=consumer_settings.listen_keys,
            callback=callback
        )



    def send_message(self, messenger_setting: MessengerSetting, data: any):
        return self.publish(
            data=data,
            routing_key=messenger_setting.key,
            exchange=messenger_setting.service_name
        )



