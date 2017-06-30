
""" This package contains publisher for different topics. Publisher/Subscriber
    pattern is implemented using
    `Autobahn Websockets <http://autobahn.ws/python/websocket/programming.html>`_.

    The pub/sub pattern works this way: You have three entities:

    * An broker
    * Publisher
    * Subscriber

    Publisher publish content to a specific topic to a broker. Subscriber
    subscribe for a specific topic at the broker. Role of the broker in our case
    is a WAMP router, i.e. *crossbar.io*. Publisher and subscriber are thus
    decoupled from each other, they can even be implemented in different
    programming languages.

    The nice thing for us: We do not have to take care distributing content
    ourselves so it easily scales and additional security can be implemented
    pretty easy.
"""
from autobahn.asyncio.websocket import WebSocketServerProtocol,WebSocketServerFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol
from autobahn.asyncio.websocket import WebSocketClientFactory
import trollius as asyncio
import json


from threading import Thread
import Queue

import logging,csv,time
logging.basicConfig()


class WebSockServerFactory(WebSocketServerFactory):
    """ Each time a connection is created, factory produces a new instance of
        its ``WebSocketServerProtocol``. The Server is the connection, so to
        speak and the factory the actual server.

        Note:
            The factory here acts as the broker in the pub/sub pattern. Publisher
            publish their data to the ServerFactory and the factory takes care
            of distributing it to the subscriber.
    """
    def __init__(self, *args, **kwargs):
        WebSocketServerFactory.__init__(self, *args, **kwargs)
        self.clients = []
        self.subscriptions = {}

    """ Register the new connected Client """
    def register(self, client):
        self.clients.append(client)

    """ UnRegister the Client on disconnect """
    def unregister(self, client):
        self.unsubscribe(client)
        if client in self.clients:
            self.clients.remove(client)        

    """ Subscibe the Client to a certain topic """
    def subscribe(self, client, topic):
        print("Client subscribed to %s" % (topic))
        if not topic in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(client)        

    """ UnSubscibe the Client from a topic """
    def unsubscribe(self, client, topic=None):
        if topic is None:
            for topic in self.subscriptions:
                for c in self.subscriptions[topic]:
                    if c == client:                        
                        self.subscriptions[topic].remove(c)
                        break               
        else:
            if topic in self.subscriptions:
                for c in self.subscriptions[topic]:
                    if c == client:
                        self.subscriptions[topic].remove(c)
                        break    
    """ Publish a topic with data
        This sends the data to all Clients that subscribed to this topic
    """
    def publish(self, topic, data=""):  
        # If topic does not exist
        if topic not in self.subscriptions.keys():
            #logging.info('No subscriptions for topic: {}'.format(topic))
            return
            
        # If no client in topic list
        if len(self.subscriptions[topic]) == 0:
            return
            
        #print("Publishing %s" % (topic),data)
        message = {'topic':topic,'data': data}
        msg = json.dumps(message)
        for c in self.subscriptions[topic]:
            c.sendMessage(msg)

    def sendAll(self, data):
        message = {'data': data}
        msg = json.dumps(message)
        for c in self.clients:
            c.sendMessage(msg)


class WebSockServer(WebSocketServerProtocol):
    def __init__(self):
        """ Initializes object
        """
        super(WebSockServer, self).__init__()
        self._topic = None

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.factory.register(self)

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary received: {0} bytes".format(len(payload)))
        else:
            msg = json.loads(payload.decode('utf8'))
            method = msg['method']
            topic = msg['topic'] if 'topic' in msg else None
            data = msg['data'] if 'data' in msg else None

            if method == 'subscribe':
                self.factory.subscribe(self, topic)
            elif method == 'publish':
                self.factory.publish(topic, data)
            else:
                raise KeyError('Method {} not known to WebSockServer'.format(method))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason),code)
        self.factory.unregister(self)


class WebSocketServer(Thread):
    def __init__ (self,ip="localhost",port=8080):
        Thread.__init__(self)
        self.ip = ip
        self.port = port

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.factory = WebSockServerFactory("ws://%s:%d" % (self.ip,self.port))
        self.factory.protocol = WebSockServer

        loop = asyncio.get_event_loop()
        coro = loop.create_server(self.factory, self.ip, self.port)

        self.server = loop.run_until_complete(coro)
        print("Starting Websocketserver at %s:%d" % (self.ip,self.port))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print 'Error while serving websocketserver'
            raise
        finally:
            self.server.close()
            loop.close()

    def stop(self):
        loop = asyncio.get_event_loop()
        self.server.close()
        loop.stop()


class PublisherProtocol(WebSocketClientProtocol):
    """ Protocol class for publisher clients
    """
    websocketfactory = None

    @staticmethod
    def setWebSocketFactory(factory):
        PublisherProtocol.websocketfactory = factory

    @staticmethod
    def onConnect(response):
        logging.info('Publisher client connected to broker {}'.format(response.peer))

    @staticmethod
    def onOpen():
        logging.info('Publisher client connection openend')

    @staticmethod
    def onMessage():
        logging.info('Message received on Publisher. Publisher not designed' + \
                ' for receiving messages. Will be silently discarded')

    @staticmethod
    def onClose(wasClean, code, reason):
        logging.info('WebSocket connection on publisher closed ' + \
                'due to {}'.format(reason))
    @staticmethod
    def serialize(obj):
        """ Serializes object to string
        """
        return json.dumps(obj)

    @staticmethod
    def publish(topic, data):
        if not PublisherProtocol.websocketfactory:
            logging.info('Error: No websocketfactory defined!')
            return

        PublisherProtocol.websocketfactory.publish(topic,data)

