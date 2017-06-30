import json
import warnings
import logging
import jsonrpc
import requests
from . import networkmanager_config
from . import general_config
logging.basicConfig(level=logging.DEBUG)

class NetworkmanagerFactory(object):
    """ Factory for NetworkmanagerStubs
    """
    @classmethod
    def produce(cls):
        """ Prodcues an instance of NetworkmanagerStub as configured
        """
        stub = networkmanager_config['networkmanager_stub']
        if stub == 'ovs':
            return OvsStub()
        else:
            raise KeyError('No NetworkManagerStub for {} found'.format(stub))


class NetworkmanagerStub(object):
    """ Abstract base classes for an interface towards an network manager.
        The network manager controls the vSDN, i.e. the virutal network where
        the tenant's controller are connected to HyperFLEX.

        Attributes:
            logger (logging.Logger): Classes logger object
            config (dict): Dictionary with configuration entries
    """

    def __init__(self, logger_name):
        """ Initializes object

            Args:
                logger_name (string): Name of the classes logger object
        """
        self._logger = logging.getLogger(logger_name)
        self._config = networkmanager_config

    def set_rate_limit(self, switch_id, interface, ratelimit):
        """ Sets the iingress rate of an interface on a switch in the VSDN

            Args:
                ratelimit (int): Rate interface should be set to
                interface (int): Number of the interface to police
                switch_id (int): Database primary key of switch in control plane
        """
        raise NotImplementedError(
                'Method set_interface_ingress_rate_limit not ' +
                'implemented'
                )

    def set_burst(self, swtich_id, interface, burstlimit):
        """ Sets the ingress burst limit for an switch

            Args:
                burstlimit (int): Burst limit interface should be set to
                interface (int): Number of the interface to police
                switch_id (int): Database primary key of switch in control plane
        """
        raise NotImplementedError(
                'Method set_interface_ingress_burst_rate not ' +
                'implemented'
                )


class OvsStub(NetworkmanagerStub):
    """ RPC stub for openvswitch

        Attributes:
            logger (logging.Logger): Classes logger object
            config (dict): Dictionary with configuration entries
            __next_id (int): currently highest id
    """
    __next_id = 0
    def __init__(self):
        """ Initializes object
        """
        super(OvsStub, self).__init__('OvsStub')

    @classmethod
    def __generate_id(cls):
        """ Generates ids to use for messages

            Returns:
                id: integer
        """
        cls.__next_id += 1
        return cls.__next_id

    def _send_message(self, url, method, params=None):
        """ Sends a message to rpc endpoints.

            Args:
                method (string): Method to invoke on remote system
                params (list, optional): List of parameters for the remote
                    method invocation. The order of the arguments must be
                    as in the signature of the remote method

            Returns:
                result: String

            Raises:
                AssertionError: Raised if id and received id do not match
                requests.exceptions.HTTPError: If return status of message
                    is anything other than 200
        """
        id = self.__generate_id()
        id = 0
        headers = {'content-type': 'application/json'}
        payload = {
                'method': method,
                'params': params if params is not None else [],
                'jsonrpc': '2.0',
                'id': id
                }
        if general_config['mode'] == 'debug':
            self._logger.info('I am in debug mode and do not send anything')
            response = {'result': {'data': 'You are in debug mode'}, 'id': id}
        else:
            self._logger.debug('Request {} on {}'.format(method, url))
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            # Raises error if status code is anything other than 200
            response = response.json()
        assert response['id'] == id, 'Wrong id received in OvsStub._send_message' + \
                'expected id {} but got {}'.format(id, response['id'])
        if 'error' in response['result'].keys():
            raise RuntimeError(response['result']['error'])
        return response['result']

    def set_rate_limit(self, switch_ip, switch_id, interface, ratelimit):
        """ Sets the iingress rate of an interface on a switch in the VSDN

            Note:
                It is important, that the names of the switche interfaces follow
                the notation *s#-eth#'.

            Args:
                ratelimit (int): Rate interface should be set to
                interface (int): Number of the interface to police
                switch_id (int): Database ID of switch
                switch_ip (string): IP address stored for switch in database
        """
        url = '{}{}:{}'.format(
                self._config['rpc_prefix'],
                switch_ip,
                self._config['rpc_port']
                )
        if ratelimit is None:
            ratelimit = 0
        response = self._send_message(
                url=url,
                method='ovshandler.set_interface_ingress_rate_limit',
                params=['eth{}'.format(interface), ratelimit]
                )
        return response

    def set_burst(self, switch_ip, switch_id, interface, burstlimit):
        """ Sets the ingress burst limit for an switch.

            Note:
                It is important, that the names of the switche interfaces follow
                the notation *s#-eth#'.

            Args:
                burstlimit (int): Burst limit interface should be set to
                interface (int): Number of the interface to police
                switch_id (int): Database ID of switch
                switch_ip (string): IP address stored for switch in database
        """
        url = '{}{}:{}'.format(
                self._config['rpc_prefix'],
                switch_ip,
                self._config['rpc_port']
                )

        if burstlimit is None:
            burstlimit = 0
        response = self._send_message(
                url=url,
                method='ovshandler.set_interface_ingress_burst_limit',
                params=['eth{}'.format(interface), burstlimit]
                )
        return response

