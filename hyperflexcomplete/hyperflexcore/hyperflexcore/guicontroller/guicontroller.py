#!/bin/python
""" Implements different GUIController to handle different types of GUIs
"""
import sys
import os
import time
import traceback
from werkzeug.datastructures import Headers
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)
sys.path.insert(0, path)
from hyperflexcore.data import data_config
from hyperflexcore.guicontroller import guicontroller_config
import json
import intelligence.guihandling
from data.dbinterfaces import AAAConnector
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from websocksrv import WebSocketServer,PublisherProtocol
from hyperflexcore.data.livedata import LiveDataController
#from docopt import docopt
import logging
logging.basicConfig()




class ServerFactory(object):
    """ Produces servers
    """
    @classmethod
    def produce(cls, stub=None):
        """ Produces a server based on configuration

            Raises:
                KeyError: If configured stub is not known to factory
        """
        if stub is None:
            stub = guicontroller_config['stub']
        cls = None
        if stub == 'hyperflex':
            cls = HyperFlexHandler
        else:
            raise KeyError('Stub {} is not known to ServerFactory'.format(stub))
        return JsonRpcServer(cls)



class HyperFlexHandler(object):
    def __init__(self):
        self._config = guicontroller_config
        self._handler = intelligence.guihandling.ManagementGuiControllerHandler()
        self._db_conn = AAAConnector()
        self._logger = logging.getLogger('HyperFlexHandler')

    def _align_inner_dictionary(self, dictionary):
        """ Added for directly aligning dictionary without surrounding
            list and other dictionary
        """
        rename = {
            "to_node":u"to",
            "from_node":u"from",
            "to":"to_node",
            "from":"from_node",
            "isolation": "isolation_method"
        }

        keys = dictionary.keys()
        for k in keys:
            if k in rename.keys():
                dictionary[rename[k]] = dictionary.pop(k)

        return dictionary

    def _align_key_names_for_hyperflexgui(self, dic):
        """ Renames keys in dictionary as expected by GUI

            Args:
                dic (Dcitionary): Return value from HyperFLEX intelligence
                    or dicionary passed by GUI
        """

        ignore = {}
        for pkey, list in dic.iteritems():
            if pkey == 'vsdn':
                self._align_inner_dictionary(list)
            elif pkey in ['edges', 'nodes']:
                for e in list:
                    if type(e) != dict:
                        continue
                    else:
                        self._align_inner_dictionary(e)

        if 'vsdn_id' in dic.keys():
            if type(dic['vsdn_id'] == unicode):
                dic['vsdn_id'] = int(dic['vsdn_id'])
        return dic

    def get_all_vsdn(self, user_id=1):
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
        """
        self._logger.info('RPC call get_all_vsdn')
        ret = None
        try:
            if self._db_conn.authorize(user_id, 'get_all_vsdn'):
                vsdns = self._handler.get_all_vsdn_topos()
            else:
                vsdns = self._handler.get_all_tenant_vsdn_topos(user_id)
                print vsdns
            for vsdn in vsdns:
                self._align_key_names_for_hyperflexgui(vsdn)
            ret = {'data': vsdns}
        except Exception as e:
            ret = {
                    'error': 'Error during fetching of VSDNs. ' + \
                    'Error was: {}'.format( e.message)
                    }
        return json.dumps(ret)

    def update_vsdn(self, updates):
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
                        "to_node": <id>
                        "action": (add|remove)
                    },
                    ...
                ]
        """
        self._logger.info('RPC call update_vsdn')
        dic = json.loads(updates)
        self._logger.debug(json.dumps(updates))
        self._logger.debug(json.dumps(dic, indent=1))
        user = dic.pop('user') if 'user' in dic.keys() else 2
        dic = self._align_key_names_for_hyperflexgui(dic)
        message = {}
        try:
            self._handler.process_network_change_request(dic)
            message['data'] = 'success'
        except Exception as e:
            self._logger.exception('Error during update of VSDN. ' + \
                    'Error was {}'.format(e.message))
            message['error'] = e.message
        return json.dumps(message)

    def get_physical_topo(self, user_id=2):
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
                    vsdn_id: <id>,
                    nodes: [
                        {
                            'id': <id>,
                            'type': 'switch',
                            'name': <name>,
                            'dpid': <dpid>,
                            'ip': <ip>,
                            'ip_port': <ip_port>,
                            'num_ports': <num_ports>,
                            'cplane': <True/False>
                        }
                        ...
                    ]
                    edges: [
                        {
                            'from_node': <id>,
                            'from_port': <port>,
                            'to_node': <id>,
                            'to_port': <id>
                        },
                        ...
                    ]
                }
        """
        self._logger.info('RPC call get_physical_topo')
        ret = None
        try:
            dic = self._handler.get_data_plane()
            if self._db_conn.authorize(user_id, 'hvcontext'):
                ctrl = self._handler.get_control_plane()
                dic['nodes'].extend(ctrl['nodes'])
                dic['edges'].extend(ctrl['edges'])
                hypervisor, edges = self._handler.get_hypervisor_context()
                for h in hypervisor:
                    dic['nodes'].append(h)
                dic['edges'].extend(edges)
            else:
                dic_ctrl = self._handler.get_control_plane()
                dic['nodes'].extend(dic_ctrl['nodes'])
            dic = self._align_key_names_for_hyperflexgui(dic)
            ret = {'data': dic}
        except Exception as e:
            self._logger.exception('Error during retrieval of physical topo. ' + \
                    'error was {}'.format(e.message))
            ret = {'error': e.message}
        return json.dumps(ret)

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
        self._logger.info('RPC call get_vsdn')
        ret = None
        try:
            dic = self._handler.get_vsdn_topo(vsdn_id)
            self._logger.debug('align key names')
            dic = self._align_key_names_for_hyperflexgui(dic)
            ret = {'data':dic}
            self._logger.debug(json.dumps({'data': dic}, indent=1))
        except Exception as e:
            self._logger.exception('Error during VSDN topology retrieval')
            ret = {'error': e.message}

        return json.dumps(ret)

    def request_vsdn(self, data):
        self._logger.info('RPC call request_vsdn')
        dic = json.loads(data)
        print json.dumps(dic, indent=1)

        user = dic['user']
        vsdn_data = dic['data']

        vsdn_data = self._align_key_names_for_hyperflexgui(vsdn_data)
        ret = None
        try:
            vsdn_data['vsdn']['tenant_id'] = user
            ret = self._handler.new_vsdn(vsdn_data)
            global WSS
            WSS.factory.publish("vsdn_changed")
            ret = {'data': ret}
        except Exception as e:
            ret = {'error': e.message}
        return json.dumps(ret)

    def remove_vsdn(self, vsdn_id, user=None):
        self._logger.info('RPC call remove_vsdn vsdn_id: {}, user: {}'.format(
            vsdn_id, user))
        vsdn_id = int(vsdn_id)
        tenant_id = int(user if user is not None else 1)
        ret = None
        try:
            self._handler.remove_vsdn(tenant_id, vsdn_id)
            ret = {'data': 'success'}
        except Exception as e:

            ret = {'error': e.message}
        return json.dumps(ret)

    def authenticate(self, username, password):
        """ Authenticates a user and returns possible configured VSDNs

            Args:
                username (String): Name of user
                password (String): Password of user

            Returns:
                data: Dictionary containing user's ID, role and VSDNs
                    he is able to see
        """
        self._logger.info('RPC call authenticate')
        ret = {}
        user = self._db_conn.authenticate(username, password)
        if user is None:
            self._logger.info('Authentication for user {} failed'.format(username))
            ret = json.dumps({'error': 'Autentication failed'})
        else:
            self._logger.info('Authentication for user {} succeeded'.format(username))
            tmp = json.loads(self.get_all_vsdn(user_id=user.id))
            if 'error' in tmp.keys():
                pass
            else:
                ret['user'] = {'id': user.id, 'role': user.role, 'name': user.name}
                ret['vsdns'] = tmp['data']
            ret = json.dumps({'data': ret})
        return ret

    def new_user(self, admin_id, name, password, role):
        """ Adds new user to the system.

            Args:
                admin_id (int): ID of user attempting to create new user. Must
                    be user with role admin.
                name (String): Name of new user
                password (String): Password of new user
                role (String): Role of new user
        """
        self._logger.info('RPC call new_user')
        if self._db_conn.authorize(admin_id, 'new_user'):
            user = User(name, password, role)
            db_conn.store.add(user)
            db_conn.store.flush()
            ret = {'data': {'id': user.id}}
        else:
            ret = {'error': {'Authorization failed. You are not admin'}}
        return json.dumps(ret)


class JsonRpcServer(object):
    def __init__(self, handler_cls):
        self._config = guicontroller_config
        self._handler_cls = handler_cls

    @Request.application
    def application(self, request):
        dispatcher.add_class(self._handler_cls)
        response = JSONRPCResponseManager.handle(
                request.data, dispatcher)
        headers = Headers()
        headers.add('Access-Control-Allow-Origin', '*')
        headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return Response(response.json, mimetype='application/json',
                headers=headers)

    def start_server(self):
        """ Start server and listen for requests
        """
        print self._config['request_receiver_ip'], self._config['request_receiver_port']
        run_simple(
                self._config['request_receiver_ip'],
                int(self._config['request_receiver_port']),
                self.application
                )


if __name__ == '__main__':
    """
        Starting Websocketserver
    """
    WSS = WebSocketServer(
            ip=guicontroller_config["wss_ip"],
            port=int(guicontroller_config["wss_port"])
            )
    WSS.daemon = True
    WSS.start()
    time.sleep(1)
    PublisherProtocol.setWebSocketFactory(WSS.factory)

    live_data_ctrl = LiveDataController("tcp://0.0.0.0:9874")
    live_data_ctrl.daemon = True
    live_data_ctrl.start()


    server = ServerFactory.produce('hyperflex')
    try:
        server.start_server()
    except KeyboardInterrupt as e:
        logging.exception('Hit Ctrl-C - shutting down cpu agent...')
        live_data_ctrl.stop()
        raise
    finally:
        live_data_ctrl.stop()

