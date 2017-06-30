import sys
import os
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.relpath(__file__)),
    os.path.pardir
    ))
from hyperflexcore.data.livedata import CpuAgent, LiveDataController
from hyperflexcore.data import data_config
from nanomsg import Socket, PULL
import json
import time
import logging


class CpuAgentTest(object):
    @classmethod
    def setup(cls):
        cls.url = data_config['pipeline_address']
        cls.agent = CpuAgent(cls.url)
        cls.socket = Socket(PULL)
        cls.socket.bind(cls.url)

    def test_message_sending(self):
        self.agent.start()
        for i in range(10):
            msg = self.socket.recv()
            msg_d = json.loads(msg)
            assert 'topic' in msg_d.keys(), 'topic missing'
            assert 'data' in msg_d.keys(), 'data missing'
            print msg_d['topic'], msg_d['data'], msg
        self.agent.stop()

class LiveDataControllerTest(object):
    @classmethod
    def setup(cls):
        cls.url = data_config['pipeline_address']
        cls.controller = LiveDataController(cls.url)
        cls.logger = logging.getLogger('LiveDataControllerTest')

    def test_receiving(self):
        try:
            self.logger.info('start controller')
            self.controller.start()
            time.sleep(10)
            self.logger.info('stop controller')
            self.controller.stop()
            self.logger.info('wait for controller to stop')
            self.controller.join()
        except Exception as e:
            self.logger.exception('Caught exception: {}'.format(e.message))
            self.logger.info('stop controller')
            self.controller.stop()
            self.logger.info('wait for controller to stop')
            self.controller.join()

