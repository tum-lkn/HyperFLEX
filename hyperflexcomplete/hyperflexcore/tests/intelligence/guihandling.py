""" Test Module for Embeddings
"""
import numpy
import logging
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
import hyperflexcore.intelligence.guihandling as guihandling
import hyperflexcore.data.dbinterfaces as dbi
import json
logging.basicConfig(level=logging.DEBUG)

class GuiHandlerTest(object):
    @classmethod
    def setup(cls):
        cls.handler = guihandling.ManagementGuiControllerHandler()

    def test_update_vsdn_msg_sw(self):
        update = {
                'vsdn': {
                    'id': 12,
                    'message_rate': 500
                    },
                'nodes': [],
                'edges': []
                }
        self.handler.process_network_change_request(update)

    def test_update_vsdn_msg_hw(self):
        update = {
                'vsdn': {
                    'id': 12,
                    'message_rate': 500
                    },
                'nodes': [],
                'edges': []
                }
        self.handler.process_network_change_request(update)

    def test_update_vsdn_change_sw_hw(self):
        update = {
                'vsdn': {
                    'id': 12,
                    'message_rate': 1000,
                    'isolation': 1
                    },
                'nodes': [],
                'edges': []
                }
        self.handler.process_network_change_request(update)

    def test_update_vsdn_change_hw_sw(self):
        update = {
                'vsdn': {
                    'id': 12,
                    'message_rate': 1000,
                    'isolation': 2
                    },
                'nodes': [],
                'edges': []
                }
        self.handler.process_network_change_request(update)

    def test_remove_vsdn(self):
        self.handler.remove_vsdn(1, 25)

    def test_get_vsdn_topo(self):
        ret = self.handler.get_vsdn_topo(8)
        print json.dumps(ret, indent=1)

    def test_request_vsdn(self):
        request = {
            "user": 1,
            "data": "{" + \
                "\"nodes\":[{" + \
                    "\"num_ports\":10," + \
                    "\"y\":-198," + \
                    "\"x\":253," + \
                    "\"label\":\"Berlin\"," + \
                    "\"type\":\"switch\"," + \
                    "\"id\":1" + \
                "},{" + \
                    "\"num_ports" + \
                    "\":20," + \
                    "\"y\":441," + \
                    "\"x\":103," + \
                    "\"label\":\"Munich\"," + \
                    "\"type\":\"switch\"," + \
                    "\"id\":8" + \
                "},{" + \
                    "\"type\":\"controller\"," + \
                    "\"label\":\"blablub\"," + \
                    "\"id\":\"2749b13c-ee9c-4d0a-899d-825c96d26f86\"," + \
                    "\"x\":-9,\"y\":-6" + \
                "}]," + \
                    "\"edges\":[{" + \
                    "\"from_node\":1," + \
                    "\"to_node\":8," + \
                    "\"cplane\":false," + \
                    "\"datarate\":1000" + \
                "},{"+ \
                    "\"from_node\":\"2749b13c-ee9c-4d0a-899d-825c96d26f86\"," + \
                    "\"to_node\":67," + \
                    "\"datarate\":1000," + \
                    "\"cplane\":true" + \
                "}]," + \
                "\"vsdn\": {" + \
                    "\"name\":\"Nosetest\"," + \
                    "\"ctrl_ip\":\"192.168.50.10\"," + \
                    "\"ctrl_port\":6633," + \
                    "\"subnet\":\"10.0.0.1/24\"," + \
                    "\"isolation_method\":2," + \
                    "\"ctrl_access\":67," + \
                    "\"message_rate\":500" + \
               "}" + \
            "}"
        }
        dic = json.loads(request['data'])
        dic['vsdn']['tenant_id'] = 1
        ret = self.handler.new_vsdn(dic)
        print ret
        assert type(ret) == dict, 'No Dictionary returned'
        assert 'id' in ret.keys(), 'VSDN id missing'
        assert 'usedcpu' in ret.keys(), 'Used CPU missing'
        assert 'allocatedcpu' in ret.keys(), 'Allocated CPU missing'
        assert 'bitrate' in ret.keys(), 'bitrate missing'
        assert ret['usedcpu'] != -1, 'Calculation went wrong'

