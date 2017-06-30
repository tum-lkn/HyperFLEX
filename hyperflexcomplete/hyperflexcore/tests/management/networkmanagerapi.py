import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
from management.networkmanager import OvsStub
import logging
import json
logging.basicConfig(level=logging.DEBUG)

class OvsStubTest(object):
    def test_set_rate_limit(self):
        stub = OvsStub()
        result = stub.set_interface_ingress_rate_limit('1', 1, 50)
        logging.debug(result)

    def test_set_burst(self):
        stub = OvsStub()
        result = stub.set_interface_ingress_burst_limit('1', 1, 50)
        logging.debug(result)

