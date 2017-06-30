""" Module containing testing methods for module ``guicontroller.guicontroller``
"""
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
print os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    )

from hyperflexcore.guicontroller.guicontroller import HyperFlexHandler
import json
from hyperflexcore.guicontroller import guicontroller_config
import requests

def setup_jsonrpc(method, params):
    config = guiconfig.get_config()
    url = "http://{}:{}/jsonrpc".format(
            config['request_receiver_ip'],
            config['request_receiver_port']
            )
    headers = {'content-type': 'application/json'}

    # Example echo method
    payload = {
        "method": method,
        'params': params,
        "jsonrpc": "2.0",
        "id": 0,
    }
    return url, headers, payload


def setup_outward_message():
    pass

def test_aling_key_names():
    pass

def test_get_all_vsdn():
    print 'TEST GET ALL VSDN'
    print '================='

    handler = HyperFlexHandler()
    print 'AFTER INIT'
    string = handler.get_all_vsdn()
    print 'AFTER CALL'
    lst = json.loads(string)
    print json.dumps(lst, indent=1)

def test_update_vsdn():
    request = {
            'vsdn': {
                'id': 67,
                'isolation_method': 2,
                'message_rate': 10000
                }
            }
    handler = HyperFlexHandler()
    ret = json.loads(handler.update_vsdn(json.dumps(request)))
    assert 'data' in ret.keys(), 'Failed update vsdn test'
    print ret

def test_get_physical_topo():
    pass

def test_get_vsdn():
    handler = HyperFlexHandler()
    ret = handler.get_vsdn(6,1)
    print ret

def test_aling_key_names():
    pld = {
        "nodes":[
            {"x": - 137, "num_ports":5, "y": - 266, "type":"switch", "id":3, "label":"Hamburg", "cpu":25},
            {"x": - 151, "num_ports":10, "y":140, "type":"switch", "id":5, "label":"Frankfurt", "cpu":25},
            {"x":311, "num_ports":5, "y":43, "type":"switch", "id":6, "label":"Dresden", "cpu":50},
            {"x":103, "num_ports":5, "y":441, "type":"switch", "id":8, "label":"Munich", "cpu":25},
            {"type":"controller", "label":"TESTcontroller1", "id":"asf4434ad43", "x":303, "y": - 30}
        ],
        "edges":[
            {"from_node":3, "to_node":5, "bw":500},
            {"from_node":5, "to_node":8, "bw":500},
            {"from_node":5, "to_node":6, "bw":500},
            {"from_node":9, "to_node":6, "bw":1000},
            {"from_node":'asf4434ad43', 'to_node': 9, 'bw': 1000}
        ],
        "vsdn":{
            "name": "VSDN1",
            "controller_type":"ryu",
            "controller_loc":"dresden",
            "default_bw":"1000",
            "subnet":"10.1.0.0/16",
            "isolation":"hardware"
        }
    }
    handler = HyperFlexHandler()
    handler._align_key_names_for_hyperflexgui(pld)
    print json.dumps(pld, indent=1)

def test_request_vsdn():
    print 'TEST REQUEST VSDN'
    print '================='
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
                    "\"from\":1," + \
                    "\"to\":8," + \
                    "\"cplane\":false," + \
                    "\"datarate\":1000" + \
                "},{"+ \
                    "\"from\":\"2749b13c-ee9c-4d0a-899d-825c96d26f86\"," + \
                    "\"to\":22," + \
                    "\"datarate\":1000," + \
                    "\"cplane\":true" + \
                "}]," + \
                "\"vsdn\": {" + \
                    "\"name\":\"Nosetest\"," + \
                    "\"ctrl_ip\":\"192.168.50.10\"," + \
                    "\"ctrl_port\":6633," + \
                    "\"subnet\":\"10.0.0.1/24\"," + \
                    "\"isolation\":1," + \
                    "\"ctrl_access\":22," + \
                    "\"message_rate\":500" + \
               "}" + \
            "}"
        }
    response = HyperFlexHandler().request_vsdn(json.dumps(request))
    print response
    assert type(response) is int, 'embedding failed!!!'

def test_remove_vsdn():
    print 'TEST REMOVE VSDN'
    print '================'
    #vsdn_id = int(test_request_vsdn())
    vsdn_id = 1
    print HyperFlexHandler().remove_vsdn(vsdn_id,1)
    print 'TEST DONE'
    print '---------'

def test_authenticate():
    handler = HyperFlexHandler()
    result = handler.authenticate(u'tenant1', u'tenant')
    result = json.loads(result)
    print json.dumps(result, indent=1)
    assert 'data' in result.keys(), 'authenticating tenant1 failed'


if __name__ == '__main__':
     test_get_all_vsdn()
