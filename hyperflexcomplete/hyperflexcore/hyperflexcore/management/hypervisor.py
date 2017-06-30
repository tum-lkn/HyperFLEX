import json
import warnings
from . import hypervisor_config
from . import general_config
import urllib2,ssl
import logging
logging.basicConfig(level=logging.DEBUG)

class HypervisorFactory(object):
    """ Uses factory pattern to return a class providing interfaces to
        communicate with a specific type of Hypervisor (FlowVisor, OpenVirtex...)
    """

    @classmethod
    def produce(cls, element=None):
        """ Returns ordered type of HyperVisorStub.

            Args:
                order (String): Specification of type of Hypervisor

            Returns:
                HypervisorStub

            Raises:
                ValueError if order unknown
        """
        order = hypervisor_config['hypervisor_stub']
        if order == 'flowvisor':
            if element is None:
                return FlowVisorStub.from_config()
            else:
                return FlowVisorStub.from_node(element)
        else:
            raise ValueError('Unknown keyword encountered in management.' + \
                    'backend.HypervisorFactory.produce_hypervisor for ' + \
                    'argument "order", was: {}'.format(order)
                    )
        return hypervisor_stub


class HypervisorStub(object):
    """ Base class for concrete stubs for hypervisor
    """

    def __init__(self, port, url, user, password, logger_name):
        """ Initializes object.

            Args:
                logger_name (logging.Logger): Classes logger
        """
        self._service_proxy = None
        self._what_stub = 'HypervisorStub'
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.INFO)
        self._port = port
        self._ip = url
        self._user = user
        self._password = password

    @classmethod
    def from_config(cls):
        """ Creates Stub from configuration file
        """
        config = hypervisor_config
        url = config['ip']
        user = config['user']
        port = config['port']
        password = config['password']
        return cls(port, url, user, password)

    @classmethod
    def from_node(cls, node):
        """ Creates FlowVisorStub from database object

            Args:
                node (data.dbinterfaces.Hypervisor): Object from which to
                    create stub
        """
        return cls(node.info.port, node.ip, node.info.user, node.info.password)

    def add_slice(attributes):
        raise NotImplementedError('Method add_slice not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_slices():
        raise NotImplementedError('Method list_slices not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def update_slice(updates):
        raise NotImplementedError('Method update_slice not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def remove_slice(identifier):
        raise NotImplementedError('Method remove_slice not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def update_slice_password(identifier, password):
        raise NotImplementedError('Method update_slice_password not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_flowspace(options):
        raise NotImplementedError('Method list_flowspace not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def remove_flowspace(identifier):
        raise NotImplementedError('Method remove_flowspace not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def add_flowspace(attributes):
        raise NotImplementedError('Method add_flowspace not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def update_flowspace(updates):
        raise NotImplementedError('Method update_flowspace not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_slice_info(identifier):
        raise NotImplementedError('Method list_slice_info not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_datapaths():
        raise NotImplementedError('Method list_datapaths not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_datapath_info(identifier):
        raise NotImplementedError('Method list_datapath_info not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_links():
        raise NotImplementedError('Method list_links not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_slice_status(identifier):
        raise NotImplementedError('Method list_slice_status not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )

    def list_datapath_status(identifier):
        raise NotImplementedError('Method list_datapath_status not yet implemented ' + \
                'for stub {}'.format(self._what_stub)
                )


class FlowVisorStub(HypervisorStub):
    """ Handles remote calls to a FlowVisor instance.

        Contancts JSON-RPC API of FlowVisor and parses return messages
        for further use by other components
    """

    def __init__(self, port, url, user, password):
        """ Initializes object.
        """
        super(FlowVisorStub, self).__init__(port, url, user, password, 'flowvisor_stub_logger')
        self._what_stub = 'FlowVisorStub'
        self._url = 'https://{}:{}'.format(self._ip, self._port)
        #ssl._DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
        #ssl._DEFAULT_CIPHERS += 'RSA+3DES'
        #ctx = ssl.create_default_context()
        #ctx.check_hostname = False
        #ctx.verify_mode = ssl.CERT_NONE

        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(
                None,
                self._url,
                self._user,
                self._password
                )
        #print 'url is '+self._url+'user is '+self._user+' password is '+str(self._password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        #self._opener = urllib2.build_opener(authhandler,urllib2.HTTPSHandler(context=ctx))
        self._opener = urllib2.build_opener(authhandler)
        self._logger = logging.getLogger('FlowVisorStub')
        self._logger.setLevel(logging.DEBUG)


    def build_request(self, function, data=None):
        """ Creates an request for FlowVisor JSON API

            Args:
                function (String): The remote method that should be invocated
                data (Dictionary, optional): Data needed for method

            Returns:
                urllib2.Request
        """
        body = {
                'id': 'fvctl',
                'method': function,
                'jsonrpc': '2.0'
                }
        if data is not None:
            body['params'] = data
        header = {'Content-Type': 'application/json'}
        print body
        request = urllib2.Request(self._url, json.dumps(body), header)
        return request

    def send_request(self, request):
        """ Sends an request

            Args:
                request (urllib2.Request): Request to be send

            Returns:
                Dictionary
        """
        #ssl.wrap_socket = sslwrap(ssl.wrap_socket)

        try:
            if general_config['mode'] == 'debug':
                reply = json.dumps({'result': 'You are in debug mode'})
                self._logger.info('I am in debug mode and do not send anything')
            else:
                self._logger.debug('Send request to flowvisor at {}'.format(self._url))
                reply = self._opener.open(request)
        except Exception as e:
            self._logger.exception('Unexpected Error sending FlowVisor ' +
                    ' request. Error was {}'.format(e.message))
            print 'errorrr is '+e.message
            raise RuntimeError('Unexpected Error sending FlowVisor ' +
                    ' request. Error was {}'.format(e.message))

        if general_config['mode'] == 'debug':
            deserialized = json.loads(reply)
        else:
            deserialized = json.loads(reply.read())

        if 'error' in deserialized:
            msg = 'Error while requesting on flowvisor: ' + \
                    '{}, code: {}'.format(
                            deserialized['error']['message'],
                            deserialized['error']['code']
                            )

            self._logger.exception(msg)
            raise RuntimeError(msg)
        return deserialized['result']

    def list_slices(self):
        request = self.build_request('list-slices')
        return self.send_request(request)

    def _prepare_parameters(self, params):
        """ Transforms keys in dictionaries to nomenclature used by `fvctl-json`

            Args:
                params (Dictionary): Parameters for request

            Returns:
                adapted_params
        """
        skip = ['match']
        keys = params.keys()
        for key in keys:
            if key in skip:
                continue
            if type(params[key]) == dict:
                params[key] = self._prepare_parameters(params[key])
            elif type(params[key]) == list:
                for dc in params[key]:
                    if type(dc) == dict:
                        self._prepare_parameters(dc)
            if key.find('_') != -1:
                param = params.pop(key)
                key = key.replace('_', '-')
                params[key] = param
        return params

    def add_slice(self, vsdn):
        """ Stub for adding a new slice to the flowvisor instance.

            Args:
                vsdn (data.dbinterfaces.Vsdn): Vsdn object for which to add slice
        """
        request = {
                'slice_name': vsdn.name,
                'controller_url': 'tcp:{}:{}'.format(
                    vsdn.controller.ip,
                    vsdn.controller.info.ip_port
                    ),
                'admin_contact': 'admin@contact.com',
                'password': vsdn.password,
                'flowmod_limit': -1,
                'rate_limit': -1,
                'drop_policy': 'exact',
                'recv_lldp': False,
                'admin_status': True
                }
        request = self._prepare_parameters(request)
        rqst = self.build_request('add-slice', data=request)
        return self.send_request(rqst)

    def update_slice(self, params):
        """ Stub for updating an existing slice on flowvisor.

            Args:
                params (dict): Dictionary with parameters

            Expected dictionary entries:
                slice_name: (string, required): Name of slice
                admin_contact (string, optional): Contact infor of slice admin
                controller_host (string, optional): Hostname or IP of the
                    controller of the slice
                controller_port: (int, optional): Port number of slice's controller
                drop-policy: (string, optional): Either value ``exact`` or a
                    custom rule
                recv-lldp (boolean, optional): If true, slice receives unknown
                    lldp packets
                flowmod-limit (int, optional): New value for slice tcam usage
                rate_limit (int, optional): New value for slice control
                    path rate limit
                admin-status (boolean, optional): Admin available?

            Raises:
                AssertionError if one of the requried arguments is missing
        """
        assert 'slice_name' in params.keys(), 'Argument slice_name is ' + \
                'missing in arguments for FlowVisorStub.update_slice'
        if 'rate_limit' in params.keys():
            if params['rate_limit'] is None:
                params['rate_limit'] = -1
        self._logger.debug('update slice: \n{}'.format(json.dumps(params, indent=1)))
        request = self._prepare_parameters(params)
        rqst = self.build_request('update-slice', data=request)
        return self.send_request(rqst)

    def remove_slice(self, vsdn):
        """ Removes specified slice

            Args:
                args (data.dbinterfaces.Vsdn): Vsdn object that should be removed

            Raises:
                AssertionError if mandator field is missing
        """
        args = {'slice_name': vsdn.name}
        args = self._prepare_parameters(args)
        request = self.build_request('remove-slice', data=args)
        return self.send_request(request)

    def list_datapaths(self):
        request = self.build_request('list-datapaths')
        return self.send_request(request)

    def list_flowspace(self):
        request = self.build_request('list-flowspace', data={})
        return self.send_request(request)

    def add_flowspace(self, args):
        """ Method stub for adding an flowspace

            Args:
                args (Dictionary): Dictinary with arguments for new flowspace

            Note:
                Following fields in `args` are required:
                    name (String)
                    dpid (string)
                    priority (int)
                    match (String)
                    slice_action (String)

            Raises:
                Assertion error if one of mandatory fields is missing
        """
        assert 'name' in args.keys(), 'field `name` is ' + \
            'missing (FlowVisorStub.add_flowspace)'
        assert 'dpid' in args.keys(), 'field `dipid` is missing ' + \
            '(FlowVisorStub.add_flowspace)'
        assert 'priority' in args.keys(), 'field `priority` is missing ' + \
            '(FlowVisorStub.add_flowspace)'
        assert 'match' in args.keys(), 'field `match` is missing ' + \
            '(FlowVisorStub.add_flowspace)'
        assert 'slice_action' in args.keys(), 'field `slice_action` is missing ' + \
            '(FlowVisorStub.add_flowspace)'
        print json.dumps(args, indent=1)
        request = self.build_request(
                'add-flowspace',
                data=[self._prepare_parameters(args)]
                )
        return self.send_request(request)

    def remove_flowspace(self, name):
        """ Removes specified flowspace

            Args:
                args (Dictionary): dictionary containing arguments needed for function

            Note:
                Mandatory arguments:
                    name (String): Name (id) of flowspace to be removed

            Raises:
                AssertionError if mandator field is missing
        """
        request = self.build_request('remove-flowspace', data=[name])
        return self.send_request(request)

    def list_slices(self):
        """ Queries all configured slices on FlowVisor instance

            Returns:
                slices: List of slice names
        """
        request = self.build_request('list-slices')
        ret = self.send_request(request)
        for dic in ret:
            if dic['slice-name'] == 'fvadmin':
                ret.remove(dic)
        return ret

    def wipe(self):
        """ Queries all slices configured on FlowVisor instance and deletes
            them.
        """
        slices = self.list_slices()
        for slice in slices:
            self.remove_slice({'slice_name': slice['slice-name']})

