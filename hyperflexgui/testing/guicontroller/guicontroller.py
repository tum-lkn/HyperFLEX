#!/bin/python
""" Implements different GUIController to handle different types of GUIs
"""
import sys
import os
path = os.path.dirname(os.path.realpath(sys.argv[0]))
slash_idx = path.rfind(os.path.sep)
print path[0:slash_idx + 1]
sys.path.insert(1, path[0:slash_idx + 1])

import config
import json
import time

from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import Headers
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

class HyperFlexHandler:

    def __init__(self):
        self._config = config.get_config()
        
    def get_vsdn(self, vsdn_id, user):
        """ Retuns VSDN `vsdn_id`. Contains all hosts, controller and logical
            links defined by the tenant. Does NOT include any physical switches

            Args:
                vsdn_id (int): Identifier of an VSDN network
                user (int): Identifier of entity (tenant, admin,...) requesting
                    topology (1 for admin)

            Returns:
                message (JSON serialized Dictionary): Has the following members:
                    error (String): Set if error occured. Contains error message
                    id (int): ID of request
                    data (String): JSON serialized network topology
        """
        if vsdn_id == 1:
            topo = {}
            vsdn = {}
            vsdn['id'] = '1'
            vsdn['name'] = 'vsdn_green'
            vsdn['color'] = '00ffff'
            topo['vsdn'] = vsdn

            nodes = []
            node = {}
            node['id'] = 'h1'
            node['type'] = 'host'
            node['name'] = 'host1'
            nodes.append(node)

            node = {}
            node['id'] = 'h2'
            node['type'] = 'host'
            node['name'] = 'host2'
            nodes.append(node)

            topo['nodes'] = nodes

            links = []
            link = {}
            link['from_node'] = 'h1'
            link['to_node'] = 's1'
            link['to_port'] = 3
            links.append(link)

            link = {}
            link['from_node'] = 'h2'
            link['to_node'] = 's2'
            link['to_port'] = 1
            links.append(link)

            topo['links'] = links
        else:
            topo = {}
            vsdn = {}
            vsdn['id'] = '2'
            vsdn['name'] = 'vsdn_blue'
            vsdn['color'] = '0000ff'
            topo['vsdn'] = vsdn

            nodes = []
            node = {}
            node['id'] = 'h11'
            node['type'] = 'host'
            node['name'] = 'host11'
            nodes.append(node)

            node = {}
            node['id'] = 'h12'
            node['type'] = 'host'
            node['name'] = 'host12'
            nodes.append(node)

            topo['nodes'] = nodes

            links = []
            link = {}
            link['from_node'] = 'h11'
            link['to_node'] = 's11'
            link['to_port'] = 3
            links.append(link)

            link = {}
            link['from_node'] = 'h12'
            link['to_node'] = 's11'
            link['to_port'] = 1
            links.append(link)

            topo['links'] = links

        message = {}
        message['id'] = 'some id'
        message['data'] = topo

        return json.dumps(message)

    def get_all_vsdn(self, user):
        """ Returns all VSDNs belonging to `user` (tenant, admin, ...). For each
            VSDN returns Hosts, Controller and logical links. Does NOT return
            any physical switches

            Args:
                user (int): Identifier of an entity (tenant, admin, ...) whose
                    networks (or the networks they are allowed to see) should
                    be retrieved (1 for admin).

            Returns:
                message (JSON serialized Dictionary): Has the following members:
                    error (String): Set if error occured. Contains error message
                    id (int): ID of request
                    data (List): List of JSON serialized network topologies (see
                        `wiki <https://wiki.lkn.ei.tum.de/intern:lkn:all:\
                        students:henkel2:hyperflex_centralized#dynamic_topology`)
                        
            Example:
            [
                {
                    "id":1,
                    "name":"VSDN1",
                    "color":"#ff549f",
                    "nodes":[
                        {
                            "id":"h101",
                            "label":"vSDN1_h1",
                            "type":"host"    
                        },
                        {
                            "id":"h102",
                            "label":"vSDN1_h2",
                            "type":"host"    
                        },
                        {
                            "id":"c111",
                            "label":"ctrl1",
                            "type":"controller"    
                        }
                    ],
                    "edges":[    
                        {"from":"s2","to":"h101","from_port":3,"to_port":1},    
                        {"from":"s3","to":"h102","from_port":3,"to_port":1},
                        {"from":"s3","to":"s4"},
                        {"from":"hv1","to":"c111"}
                    ]
                },
                {
                    "id":2,
                    "name":"VSDN2",
                    "color":"#54ff9f",
                    "nodes":[
                        {
                            "id":"h201",
                            "label":"vSDN2_h1",
                            "type":"host"    
                        },
                        {
                            "id":"h202",
                            "label":"vSDN2_h2",
                            "type":"host"    
                        },
                        {
                            "id":"c211",
                            "label":"ctrl2",
                            "type":"controller"    
                        }
                    ],
                    "edges":[    
                        {"from":"s2","to":"h201","from_port":4,"to_port":1},    
                        {"from":"s3","to":"h202","from_port":4,"to_port":1},
                        {"from":"s3","to":"s2"},
                        {"from":"s2","to":"s4"},
                        {"from":"hv1","to":"c211"}
                    ]
                }
        """
        vsdns = []
        
        vsdn = {
            "id":1,
            "name":"VSDN1",
            "color":"#ff549f",
            "nodes":[
                {
                    "id":101,
                    "label":"vsdn1_node1",
                    "type":"switch",
                    "x":174,
                    "y":494
                },
                {
                    "id":102,
                    "label":"vsdn1_node2",
                    "type":"switch",
                    "x":314,
                    "y":-248 
                },
                {
                    "id":111,
                    "label":"ctrl1",
                    "type":"controller",
                    "x" : 313,
                    "y" : -310     
                }
            ],
            "edges":[    
                {"from":8,"to":5},    
                {"from":5,"to":2},
                {"from":101,"to":8},
                {"from":102,"to":2},
                {"from":111,"to":102,"cplane":True}
            ]
        
        }
        vsdns.append(vsdn)
        
        vsdn = {
            "id":2,
            "name":"VSDN2",
            "color":"#54ff9f",
            "nodes":[
                {
                    "id":201,
                    "label":"vsdn2_node1",
                    "type":"switch",
                    "x":185,
                    "y":417    
                },
                {
                    "id":202,
                    "label":"vsdn2_node2",
                    "type":"switch",
                    "x":-318,
                    "y":-40    
                },
                {
                    "id":211,
                    "label":"ctrl2",
                    "type":"controller",
                    "x":-318,
                    "y":-100    
                }
            ],
            "edges":[    
                {"from":8,"to":5},    
                {"from":5,"to":4},
                {"from":201,"to":8},
                {"from":202,"to":4},
                {"from":211,"to":202,"cplane":True}
            ]
        }
        
        vsdns.append(vsdn)


        return json.dumps(vsdns)

    def alter_vsdn(self, updates):
        """ Altering VSDN (adding/removing hosts, controller, logical links)

        Args:
            updates (String): JSON serialized list of dictionaries

        Example:
            {
                'vsdn_id': <id>,
                'nodes': [
                    {
                        'type': "host",
                        'id': <id>,
                        'label': <name>,
                        'action': (add|remove)
                    }, {
                        'type': "controller",
                        'label': <name>,
                        'location': <location>,
                        'ip': <ip>,
                        'ip_port': <ip_port>,
                        'action': (add|remove)
                    }
                    ...
                ]
                'edges: [
                    {
                        "from_node": <id>,
                        "from_port": <port>,
                        "to_node": <id>
                        "to_port": <port>
                        "action": (add|remove)
                    },
                    ...
                ]
        """
        message = {}
        message['id'] = 'some id'
        message['error'] = 'Update failed <Static return message>'

        return json.dumps(message)

    def get_physical_topo(self, user):
        """ Returns physical topology based on `user`. If `user` is a tenant,
            physical ressources allocated for tenant's infrastructure are
            returned.
            If `user` is admin whole physical infrastructure (inluding
            hypervisor) is returned.
            Physical topology means switches and links between them.

            Args:
                user (int): Identifier of user (1 for admin)

            Returns:
                topology (JSON serialized List): List of Dictionaries

            Example:
                {
                    "nodes":
                    [
                        {"id":"hv1","label":"HyperVisor","type":"hypervisor"},
                        {"id":"s1","label":"S1","type":"switch","ports":5},
                        {"id":"s1","label":"S2","type":"switch","ports":5},
                        {"id":"s1","label":"S3","type":"switch","ports":5}
                    ],
                    "edges":
                    [
                        {from: "hv1", to: "s1"},
                        {from: "s1", to: "s2", from_port: 1, to_port: 1},
                        {from: "s1", to: "s3", from_port: 2, to_port: 1},
                        {from: "s2", to: "s3", from_port: 2, to_port: 2}
                    ]
                }
        """
        topo = {}
        nodes = []
        links = []
        
        if user in ["hypervisor","admin"]:
            node = {
                "id": 1,
                "label": "HyperFlex",
                "type": "hypervisor",            
                "ip": "192.168.0.1",
                "x" : -50,
                "y" : 0
                
            }
            nodes.append(node)
        
        node = {
            "id": 2,
            "label": "Berlin",
            "type": "switch",
            "dpid": "00:00:00:00:00:01",
            "ip": "192.168.0.1",
            "num_ports": 5,
            "cplane": False,
            "x" : 253,
            "y" : -198
        }
        nodes.append(node)
        
        node = {
            "id": 3,
            "label": "Hamburg",
            "type": "switch",
            "dpid": "00:00:00:00:00:02",
            "ip": "192.168.0.2",
            "num_ports": 5,
            "cplane": False,
            "x" : -137,
            "y" : -266
        }
        nodes.append(node)
        
        node = {
            "id": 4,
            "label": "Cologne",
            "type": "switch",
            "dpid": "00:00:00:00:00:03",
            "ip": "192.168.0.3",
            "num_ports": 5,
            "cplane": False,
            "x" : -257,
            "y" : 25
        }        
        nodes.append(node)
        
        node = {
            "id": 5,
            "label": "Frankfurt",
            "type": "switch",
            "dpid": "00:00:00:00:00:04",
            "ip": "192.168.0.4",
            "num_ports": 10,
            "cplane": False,
            "x" : -151,
            "y" : 140
        }        
        nodes.append(node)
        
        node = {
            "id": 6,
            "label": "Dresden",
            "type": "switch",
            "dpid": "00:00:00:00:00:05",
            "ip": "192.168.0.5",
            "num_ports": 5,
            "cplane": False,
            "x" : 311,
            "y" : 43
        }        
        nodes.append(node)
        
        node = {
            "id": 7,
            "label": "Stuttgart",
            "type": "switch",
            "dpid": "00:00:00:00:00:06",
            "ip": "192.168.0.6",
            "num_ports": 5,
            "cplane": False,
            "x" : -89,
            "y" : 382
        }        
        nodes.append(node)  

        node = {
            "id": 8,
            "label": "Munich",
            "type": "switch",
            "dpid": "00:00:00:00:00:07",
            "ip": "192.168.0.7",
            "num_ports": 5,
            "cplane": False,
            "x" : 103,
            "y" : 441
        }        
        nodes.append(node)            
        

        if user in ["hypervisor","admin"]:
            link = {"from": 1, "to": 5}
            links.append(link)
        link = {"from": 5, "to": 2, "from_port": 1, "to_port": 1}
        links.append(link)
        link = {"from": 5, "to": 3, "from_port": 2, "to_port": 1}
        links.append(link)
        link = {"from": 5, "to": 4, "from_port": 3, "to_port": 1}
        links.append(link)
        link = {"from": 5, "to": 6, "from_port": 4, "to_port": 1}
        links.append(link)
        link = {"from": 5, "to": 7, "from_port": 5, "to_port": 1}
        links.append(link)
        link = {"from": 5, "to": 8, "from_port": 6, "to_port": 1}
        links.append(link)
        link = {"from": 3, "to": 2, "from_port": 2, "to_port": 2}
        links.append(link)
        link = {"from": 8, "to": 7, "from_port": 2, "to_port": 2}
        links.append(link)
        
        

        
        topo['nodes'] = nodes
        topo['edges'] = links
        return json.dumps(topo)
    
    def request_vsdn(self, user, data):
        time.sleep(2);
        return True
    

class JsonRpcServer(object):

    def __init__(self):
        self._config = config.get_config()

    @Request.application
    def application(self, request):
        dispatcher.add_class(HyperFlexHandler)        
        response_json = JSONRPCResponseManager.handle(
                request.data, dispatcher)
        headers = Headers()
        headers.add('Access-Control-Allow-Origin', '*')
        headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return Response(response_json.json, mimetype='application/json',headers=headers)

    def start_server(self):
        """ Start server and listen for requests
        """
        run_simple(
                self._config['request_receiver_ip'],
                self._config['request_receiver_port'],
                self.application
                )

if __name__ == '__main__':
    server = JsonRpcServer()
    server.start_server()
