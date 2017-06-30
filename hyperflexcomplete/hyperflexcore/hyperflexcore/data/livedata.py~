""" Implements live data functionality. Live data is distributed using nanomsg
    and the pipeline pattern.
    The DataHandler class resides in the core and is the endpoint (pull) of the
    pipeline. The nodes gathering data (push worker) send them to this central
    end point.
    The end point then uses publisher/subscriber pattern to distribute the data
    to GUIs and also forwards it to the intelligence thread.
"""
import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
from hyperflexcore.data import data_config
from nanomsg import Socket
from nanomsg import PULL
from nanomsg import PUSH
from nanomsg import NanoMsgAPIError
import Queue
import threading
import subprocess
import psutil
import logging
import time
import json
logging.basicConfig(level=logging.DEBUG)

class LiveDataController(threading.Thread):
    """ Broker between data Agents, GUIs and central intelligence
    """
    def __init__(self, url):
        """ Initializes object

            Args:
                url (string): Socket where DataAgents should send gathered
                    data to.
        """
        from hyperflexcore.guicontroller.websocksrv import PublisherProtocol
        super(LiveDataController, self).__init__()
        self._stop = threading.Event()
        self._puller = PullWorker(url, self._stop)
        self._topics = []
        self._publisher = PublisherProtocol
        self._logger = logging.getLogger('LiveDataController')

    def run(self):
        """ Thread start method
        """
        self._puller.start()
        counter = 0
        while True:
            if self.stopped:
                break
            dic = self._puller.next_message()
            dic['method'] = 'publish'
            # Send it to central intelligence
            try:
                val = -1
                if type(dic['data']) == list:
                    cpu = dic['data'][0]
                    num_cpus = dic['data'][1]
                    val = cpu / num_cpus
                else:
                    val = dic['data']
                self._publisher.publish(dic['topic'], val)
            except Exception as e:
                logging.exception('Error while manipulating data.' + \
                        'data was: {}'.format(dic['data']))

    def stop(self):
        """ Stops the thread by setting stop event
        """
        self._stop.set()

    @property
    def stopped(self):
        """ Whether Thread has been stopped or not.

            Returns:
                True if Thread is stopped else False
        """
        return self._stop.is_set()


class PullWorker(threading.Thread):
    """ End point of pipeline
    """
    def __init__(self, url, event):
        """ Initializes object

            Args:
                url (String): Url to bind to
        """
        super(PullWorker, self).__init__()
        self._socket = Socket(PULL)
        self._url = url
        self._socket.bind(self._url)
        self._queue = Queue.Queue()
        self._stop = event

    def receive(self):
        """ Reveives message
        """
        raw_msg = self._socket.recv()
        parsed = {}
        try:
            parsed = json.loads(raw_msg)
        except:
            logging.exception(
                'PullWorker: Received msg could not be JSON parsed %s'
                 % raw_msg)                
        return parsed

    def run(self):
        """ Thread run method
        """
        while not self._stop.is_set():
            dic = self.receive()
            self._queue.put(dic)
        self.__exit__()

    def next_message(self):
        """ Return next message of queue

            Returns:
                message: Dictionary representing send message
        """
        msg = self._queue.get()
        self._queue.task_done()
        return msg

    def __enter__(self):
        """ Statement used for the `` with ... as ...:`` returns
            the object to use in the ``with`` block

            Returns:
                PullWorker
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Executed when leaving ``with`` block, regardless whether
            because of an exception or normal program flow
        """
        self._socket.close()


class PushWorker(threading.Thread):
    """ Pushes data into pipeline

        Attributes:
            url: String specifying endpoint socket connects to.
            topic: String specifying topic worker is relying data to
            samplingrate: Integer specifying the rate at which samples are
                collected in Herz [1/s]
            socket: Nanomsg socket object
            stop: threading.Event to stop Thread

        Note:
            url must be of the form ``<protocol>://<address>`` where
            ``<protocol>`` can have to following values:
            - **tcp** - send data over computer network using tcp protocol. In
              this case ``<address>`` has to be a valid IPv4 address of the
              form ``<ipv4>:<port>``
            - **inproc** - Share data between threads of the same process using
              shared memory. In this case ``<address>`` can be an arbitrary string.
            - **ipc** - Share data between two processes using a file. In
              this case ``<address>`` can be an arbitrary string.
    """

    def __init__(self, url, topic, loggername, samplingrate=100, retry_interval=1):
        """ Initializes object

            Args:
                url (string): specifying endpoint socket connects to.
                topic (String): specifying topic worker is relying data to.
                samplingrate (int): specifying the rate at which samples are
                    collected in Herz [1/s].
        """
        super(PushWorker, self).__init__()
        self._samplingrate=samplingrate
        self._socket = Socket(PUSH)
        self._url = url
        self._topic = topic
        self._socket.connect(self._url)
        self._logger = logging.getLogger(loggername)
        self._name = loggername
        self._stop = threading.Event()

    def send(self, data):
        """ Sends message into queue
        """
        message = json.dumps({
                'topic': self._topic,
                'data': data
                })
        self._socket.send(message)

    def _get_data_point(self):
        """ Message to retrieve one datapoint
        """
        raise NotImplementedError('Method get_data_point not implemented for ' + \
                'PushWorker')

    def run(self):
        """ Run method for thread
        """
        for datapoint in self._get_data_point():
            self.send(datapoint)
            self._logger.debug('topic: {} value: {} target: {}'.format(
                self._topic,
                datapoint,
                self._url
                ))
            time.sleep(1./self._samplingrate)
            if self.stopped:
                self._logger.info('{} is going down...'.format(self._name))
                break
        self.__exit__()

    def stop(self):
        """ Stops thread
        """
        self._stop.set()

    @property
    def stopped(self):
        """ Checks whether Thread is stopped.

            Returns
                True if thread stopped else False
        """
        return self._stop.is_set()

    def __enter__(self):
        """ Statement used for the `` with ... as ...:`` returns
            the object to use in the ``with`` block

            Returns:
                PushWorker
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ Executed when leaving ``with`` block, regardless whether
            because of an exception or normal program flow
        """
        self._socket.close()


class CpuAgent(PushWorker):
    """ Samples CPU utilization and pushes it into queue.

        Attributes:
            url: String specifying endpoint socket connects to.
            topic: String specifying topic worker is relying data to
            samplingrate: Integer specifying the rate at which samples are
                collected in Herz [1/s]
            retry_interval: Float specifying the interval worker tries to find
                a flowvisor instance among programs
            socket: Nanomsg socket object

        Note:
            url must be of the form ``<protocol>://<address>`` where
            ``<protocol>`` can have to following values:
            - **tcp** - send data over computer network using tcp protocol. In
              this case ``<address>`` has to be a valid IPv4 address of the
              form ``<ipv4>:<port>``
            - **inproc** - Share data between threads of the same process using
              shared memory. In this case ``<address>`` can be an arbitrary string.
            - **ipc** - Share data between two processes using a file. In
              this case ``<address>`` can be an arbitrary string.
    """
    def __init__(self, url, topic_suffix='', samplingrate=100, retry_interval=1):
        """ Initializes object

            Args:
                url (string): specifying endpoint socket connects to.
                topic (String): specifying topic worker is relying data to.
                samplingrate (int): specifying the rate at which samples are
                    collected in Herz [1/s].
                retry_interval (float): specifying the interval worker tries to
                    find a flowvisor instance among programs.
        """
        super(CpuAgent, self).__init__(
                url=url,
                topic='cpu' + topic_suffix,
                loggername='CpuAgent',
                samplingrate=samplingrate
                )
        self._retry_interval = retry_interval

    def _get_fw_pid(self):
        """ Gets pid of flowvisor process

            Uses ``subprocess`` and ``grep`` to filter running processes
            after flowvisor process

            Returns:
                pid

            Raises:
                OSError if subprocess fails
                AssertionError if returned value is not of type int
        """
        pid = None
        try:
            ret = subprocess.check_output(
                [
                    "ps aux | grep -v  aux | grep java | grep flowvisor | awk '{print $2}'"
                ],
                shell=True,
                stderr=subprocess.STDOUT
                )
        except subprocess.CalledProcessError as e:
            self._logger.exception('Error during executing subprocess command')
            msg = 'subprocess.CalledProcessError: Command {} ' + \
                            'returned nonzero exit status {} '.format(
                                e.cmd,
                                e.output
                                )
            raise OSError(msg)

        try:
            pid = int(ret.strip())
        except Exception as e:
            self._logger.exception('PID of flowvisor process could not be' +
                    'retrieved')
            msg = 'PID of flowvisor process could not be be retrieved. ' + \
                    'returned value was "{}"'.format(ret.strip())
            raise AssertionError(msg)

        return pid

    def _get_data_point(self):
        """ Message to retrieve one datapoint

            Yields:
                cpu: Integer specifying cpu utilization
        """
        def get_pid():
            """ Periodically poll for new instance of flowvisor process
            """
            while True:
                try:
                    pid = self._get_fw_pid()
                    self._logger.info('Retrieved PID {} for flowvisor'.format(pid))
                    return pid
                except AssertionError as e:
                    self._logger.info('Retry pid retrieval...')
                    time.sleep(self._retry_interval)

        pid = get_pid()
        proc = psutil.Process(pid)
	dic = {}
        while True:
            try:
                cpu = proc.get_cpu_percent()
                num_cpus = psutil.NUM_CPUS
                yield [cpu, num_cpus]
            except psutil.NoSuchProcess as e:
                self._logger.exception(
                        (
                            'PID {} does not exist anymore. Try to find' + \
                            'new instance of flowvisor...'
                            ).format(pid)
                        )
            except Exception as e:
                self._logger.exception('Unexpected exception: {}'.format(e.message))
                raise e

                #mem = proc.memory_percent()
                #num_threads = proc.num_threads()
                #t = time.time()
                pid = get_pid()
                proc = psutil.Process(pid)


if __name__ == '__main__':
    skip = False
    suf = ''
    try:
        arg = sys.argv[1]
        suf = arg[arg.find('=') + 1:].strip(' ')
    except Exception as e:
        print 'Usage:'
        print 'livedata.py suffix=<sfx>'
        print ''
        raise ArgumentError('wrong cmd arg')
    print suf
    thread = CpuAgent(url=data_config['pipeline_address'], samplingrate=2, topic_suffix=suf)
    thread.daemon = True
    thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        logging.exception('Hit Ctrl-C - shutting down thread...')
        thread.stop()
        raise        

