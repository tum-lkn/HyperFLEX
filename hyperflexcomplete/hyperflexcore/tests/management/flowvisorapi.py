import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
from hyperflexcore.management.hypervisor import FlowVisorStub
from hyperflexcore.data.dbinterfaces import Vsdn, Controller, NetworkNode
import logging
import json
import time

logging.basicConfig(level=logging.DEBUG)

class TestInfo(object):
    def __init__(self, port):
        self.ip_port = port


class TestController(object):
    def __init__(self, ip, port):
        self.info = TestInfo(port)
        self.ip = ip


class TestVsdn(object):
    def __init__(self, name, subnet, password, message_rate, controller):
        self.name = name
        self.subnet = subnet
        self.password = password
        self.controller = controller
        self.message_rate = message_rate


class TestFlowVisorStub(object):
    @classmethod
    def setup(cls):
        cls.stub = FlowVisorStub(
                port=8081,
                url='10.162.149.241',
                user='fvadmin',
                password=''
                )
        cls.vsdn = TestVsdn(
                name=u'TESTSLICE',
                subnet=u'10.0.0.0/24',
                password=u'',
                message_rate=1000,
                controller=TestController(ip='192.168.50.10', port=6633)
                )
        cls.logger = logging.getLogger('TestFlowVisorStub')

    def test_add_slice(self):
        attributes = {
                'slice_name': self.vsdn.name,
                'controller_url': 'tcp:192.168.50.10:6633',
                'admin_contact': 'admin@test.com',
                'password': 'test'
                }
        msg = self.stub.add_slice(self.vsdn)
        logging.info('Request done. Answer was {}'.format(msg))

    def test_remove_slice(self, addslice=False):
        if addslice:
            self.test_add_slice()
        args = {'slice_name': self.vsdn.name}
        msg = self.stub.remove_slice(args)
        self.logger.info('Request done. Answer was {}'.format(msg))

    def test_update_slice(self):
        params = {
                'slice_name': self.vsdn.name,
                'rate_limit': self.vsdn.message_rate
                }
        self.stub.update_slice(params)
        self.logger.info('test_update_slice, slice updated')

    def test_add_flowspace(self, addslice=True, removeslice=True):
        args = {
                'name': 'TESTSPACE1',
                'dpid': '00:00:00:00:00:00:00:01',
                'priority': 100,
                'match': {
                    'nw_dst': self.vsdn.subnet,
                    'nw_src': self.vsdn.subnet
                    },
                'slice_action': [
                    {
                        'slice_name': 'TESTSLICE',
                        'permission': 7
                    }]
                }
        if addslice:
            self.test_add_slice()
        msg = self.stub.add_flowspace(args)
        self.logger.info('Request done. Answer was {}'.format(msg))

        msg = self.stub.list_flowspace()
        logging.info('Current flowspace: {}'.format(msg))

    def test_remove_flowspace(self):
        fws = FlowVisorStub()
        msg = fws.remove_flowspace('TESTSPACE')
        logging.info('Returned message was: {}'.format(str(msg)))

    def test_message_rate(self):
        """ Simulates Request of a VSDN to check if the requested rate is
            actually set.
            Sets up a slice on flowvisor. Checking the rate has to be done
            separately using perfbench
        """
        self.test_add_slice()
        self.logger.info('slice {} added'.format(self.vsdn.name))
        self.test_add_flowspace(False, False)
        self.logger.info('Flowspace set')
        time.sleep(3)
        self.test_update_slice()
        self.logger.info('messagerate set')

if __name__ == '__main__':
    TestFlowVisorStub().test_add_slice()

