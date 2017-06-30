from werkzeug.datastructures import Headers
from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
import subprocess
import logging
from . import networkmanager_config
logging.basicConfig(level=logging.DEBUG)

class ServerFactory(object):
    """ Produces servers
    """
    @classmethod
    def produce(cls):
        """ Produces a server based on configuration

            Raises:
                KeyError: If configured stub is not known to factory
        """
        stub = networkmanager_config['stub']
        cls = None
        if stub == 'ovs':
            cls = OvsHandler
        else:
            raise KeyError('Stub {} is not known to ServerFactory'.format(stub))
        return JsonRpcServer(networkmanager_config, cls)


class OvsHandler(object):
    """ Handler providing remote methods for OpenVSwitch management
    """
    def set_interface_ingress_rate_limit(self, interface, ratelimit):
        """ Sets the ingress burst limit for an switch

            Args:
                burst_limit (int): Burst limit interface should be set to
                switch_id (int): Database primary key of switch in control plane
        """
        ret = {}
        try:
            output = subprocess.check_output(
                    'sudo ovs-vsctl set interface {} ingress_policing_rate={}'.format(
                        interface,
                        ratelimit
                        ),
                    shell=True,
                    stderr=subprocess.STDOUT
                    )
            ret['message'] = output
        except subprocess.CalledProcessError as e:
            ret['error'] = (
                    'CalledProcessError in OvsHandler.set_interface_' + \
                    'ingress_rate_limit: {}. Output of called process was {}.' + \
                    'Exit code of called process was: {}'
                    ).format(e.message, e.output, e.returncode)
            ret['message'] = e.output
        except Exception as e:
            ret['error'] = (
                    'Unexpected error in OvsHandler.set_interface_' + \
                    'ingress_rate_limit: {}'
                    ).format(e.message)
        return ret

    def set_interface_ingress_burst_limit(self, interface, burstlimit):
        """ Sets the ingress burst limit for an switch

            Args:
                burst_limit (int): Burst limit interface should be set to
                switch_id (int): Database primary key of switch in control plane
        """
        ret = {}
        try:
            output = subprocess.check_output(
                    'sudo ovs-vsctl set interface {} ingress_policing_burst={}'.format(
                        interface,
                        burstlimit
                        ),
                    shell=True,
                    stderr=subprocess.STDOUT
                    )
            ret['message'] = output
        except subprocess.CalledProcessError as e:
            ret['error'] = (
                    'CalledProcessError in OvsHandler.set_interface_' + \
                    'ingress_rate_limit: {}. Output of called process was {}.' + \
                    'Exit code of called process was: {}'
                    ).format(e.message, e.output, e.returncode)
            ret['message'] = e.output
        except Exception as e:
            ret['error'] = (
                    'Unexpected error in OvsHandler.set_interface_' + \
                    'ingress_rate_limit: {}'
                    ).format(e.message)
        return ret


class JsonRpcServer(object):
    """ Endpoint for JsonRPC requests from management package

        Attributes:
            config (dict): Dictionary with config entries
            logger (logging.Logger): Logging channel for object
            handlerclass (class): Class providing remote methods
    """
    def __init__(self, config, handlerclass):
        """ Initializes object.

            Args:
                handler (class): Class providing remote methods
                config (dict): Dictionary with config entries
        """
        self._config = config
        self._logger = logging.getLogger('JsonRpcServer')
        self._handlerclass = handlerclass

    @Request.application
    def application(self, request):
        dispatcher.add_class(self._handlerclass)
        response = JSONRPCResponseManager.handle(
                request.data,
                dispatcher
                )
        headers = Headers()
        headers.add('Access-Control-Allow-Origin', '*')
        headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return Response(
                response.json,
                mimetype='application/json',
                headers=headers
                )

    def start_server(self):
        """ Start server and listen for requests
        """
        self._logger.info('Start Management-JsonRPC Server at {}:{}'.format(
                self._config['mgmt_jsonrpc_server_ip'],
                self._config['mgmt_jsonrpc_server_port']
                ))

        run_simple(
                self._config['mgmt_jsonrpc_server_ip'],
                int(self._config['mgmt_jsonrpc_server_port']),
                self.application
                )
                
if __name__ == '__main__':
    server = ServerFactory.produce()
    server.start_server()
    

