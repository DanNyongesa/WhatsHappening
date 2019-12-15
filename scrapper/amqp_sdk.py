import pika
import logging

class DundaaAMQPSDKException(Exception): pass

class DundaaAMQPSDK():
    """
    SDK to handle connection to rabbitAMQP
    """
    def __init__(self, amqp_url=None, amqp_host=None):
        if amqp_host is None and amqp_url is None:
            raise RuntimeError("Could not initalise SDK. set either amqp_url or amqp_host")
        self._channel = None
        self._connection = None
        self.amqp_url = amqp_url
        self.amqp_host =amqp_host
        self._logger = logging.getLogger(self.__class__.__name__)

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

    def publish(self, exchange_type: str, routing_key: str, data: str, exchange=''):
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
