""" This package handles Data and Database related tasks:

    * Interfaces relation databases using Canonical's Object Relational Mapper *Storm*
    * Provides interface to store real-time data into database
    * Interface to push data from database to *HyperFLEX GUI*

    For high-level design and Software-Engineering artifacts refer to the
    `Link wiki <https://wiki.lkn.ei.tum.de/intern:lkn:all:students:kalmbach:start>`

    For more information on *Strom* refer to:

    * `Strom Tutorial <https://storm.canonical.com/Tutorial#References_and_subclassing>`_
    * `Strom Manual <https://storm.canonical.com/Manual>`_
    * Explanation on how to use `infoheritance <https://storm.canonical.com/Infoheritance>`_
      to handle inheritance in RDBMS
    * `API Documentation <https://twistedmatrix.com/users/radix/storm-api/storm.html>`_

    Convention in this module is that evertying *cursive* relates to the database
    schema and everthing ``monospace`` to python code.
"""

from . import data_config
import warnings
import time
import random
import logging
import storm.database as sdb
sdb.DEBUG = True
import storm.locals as storm
import cPickle as pkl
logging.basicConfig(level=logging.DEBUG)
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

class IterMixin(object):
    """ Base class providing subclasses with ability to return an iterator
        over their attributes
    """

    def __init__(self):
        # Filter for attributes. return only those for which filter are true
        self._filter = [
                lambda k, v: False if callable(v) else True,
                lambda k, v: False if k.startswith('_') else True
                ]

    def __iter__(self):
        """ Give an iterator over attributes

            Returns:
                Iterator
        """
        for key, value in self.__class__.__dict__.iteritems():
            for filter in self._filter:
                if not filter(key, value):
                    break
            else:
                # If foor loop terminates normally (i.e. no break) this is
                # executed (so when all tests are passed)
                yield key, value

    def to_dictionary(self):
        return dict(self)


class SwitchToVsdn(IterMixin):
    """ ORM for table *SwitchToVsdn* in database *HyperFlexTopology*

        Attributes:
            __storm_table__: String defining relation in database
            id: Integer being primary key of relation
            switch_id: Integer being foreign key of relation *PhysicalSwitch*
            vsdn_id: Integer bein foreign key for relation *Vsdn*
    """
    __storm_table__ = 'SwitchToVsdn'
    id = storm.Int(primary=True)
    switch_id = storm.Int()
    vsdn_id = storm.Int()

    def __init__(self, switch_id, vsdn_id):
        """ Inits class

            Args:
                switch_id (int): Foreign key for *PhysicalSwitch* relation
                vsdn_id (int): Foreign key for *Vsdn* relation
        """
        self.switch_id = switch_id
        self.vsdn_id = vsdn_id

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                Dictionary
        """
        return dict(self)


class LogicalEdgeEmbedding(IterMixin):
    """ ORM for table *LogicalEdgeEmbedding* in database *HyperFlexTopology*.
        One object represents a part of a logical link embedding.
        This class/relation resolves many-to-many relation, since one logical
        link may consist of multiple physical edges and one physical edge may
        be part of multiple logical links.

        Attributes:
            __storm_table__: String defining referenced relation in database
            id: Integer being primary key of relation
            logical_edge_id: Integer being foreign key of relation *LogicalEdge*.
                Specifies logical edge record is embedding
            physical_edge_id: Integer being foreign key of relation *PhysicalEdge*.
                Specifies physical edge being part of the logical edge embedding
    """
    __storm_table__ = 'LogicalEdgeEmbedding'
    id = storm.Int(primary=True)
    logical_edge_id = storm.Int()
    physical_edge_id = storm.Int()

    def __init__(self, logical_edge_id, physical_edge_id):
        """ Initializes class

            Args:
                logical_edge_id (int): Foreign key to relation *LogicalEdge*
                physical_edge_id (int): Foreign key to relation *PhysicalEdge*
        """
        super(LogicalEdgeEmbedding, self).__init__()
        self.logical_edge_id = logical_edge_id
        self.physical_edge_id = physical_edge_id

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                Dictionary
        """
        return dict(self)


class PhysicalPort(IterMixin):
    """ ORM for table *PhysicalPort* belonging to **one** *PhysicalSwitch*.

        Attributes:
            __storm_table__: String specifying relation class is referencing
            id: Integer being primary key of relation
            switch_id: Integer being foreign key to relation *PhysicalSwitch*
            number: Integer specifying the order of the port (Port1, Port2, ...)
            speed: Float specifying the data rate of the port
    """
    __storm_table__ = 'PhysicalPort'
    id = storm.Int(primary=True)
    switch_id = storm.Int()
    number = storm.Int()
    speed = storm.Float()

#    switch = storm.Reference(switch_id, PhysicalSwitch.id)

    def __init__(self, switch_id, number, speed=None):
        """ Initializes object

            Args:
                switch_id (int): Foreign key to relation *PhysicalSwitch*
                number (int): Number assigned to the port (its order)
                speed (float, optional): Data rate of the port

            Note:
                If speed is not set a random value from the interval [1;1000]
                is assigned.
                This behaviour is implemented for the start and will be removed
                as the project proceeds. Speed of the port will then also become
                a required argument.
        """
        super(PhysicalPort, self).__init__()
        self.switch_id = switch_id
        self.number = number
        if speed is None:
            random.seed(self.switch_id)
            self.speed = random.randrange(1, 1000)
        else:
            self.speed = speed

    def to_dictionary(self):
        """ Return class attributes as dictionary

            Returns:
                Dictionary
        """
        return dict(self)

network_node_info_types = {}
""" Stores mapping number --> class, i.e. for a number representing the
    info type dictionary gives the class
"""

def register_network_node_info_type(info_type, info_class):
    """ Registers a new info class (i.e. a new subclass of *NetworkNode*

        Args:
            info_type (int): *"Primary Key"* to reference a subclass of *NetworkNode*
            info_class (Class): Subclass of *NetworkNode* to be registered

        Raises:
            RuntimeError if ``info_type`` already exists
    """
    existing_info_class = network_node_info_types.get(info_type)
    if existing_info_class is not None:
        raise RuntimeError('{} hast the same info type as {}'.format(
            info_class, existing_info_class
            ))
    network_node_info_types[info_type] = info_class
    info_class.info_type = info_type


class NetworkNode(IterMixin, storm.Storm):
    """ ORM for relation *NetworkNode*. Implements inheritance for relation
        databases using *infoheritance* pattern.
        Base class for various types of network nodes such as switches, hosts,
        controller or hypervisor

        Attributes:
            __storm_table__: String defining relation class is referencing
            id: Integer being primary key of the relation. This is also the
                primary key for all subclasses of *NetworkNode*
            label: String being a human readable name of the network node.
            ip: String being IPv4 Address of the network node
            info_type: Integer being the identifier with which the subclass was
                registered.
            _info: Object being the instance of the subclass specified by
                *info_type*

        Note:
            This implements inheritance of relations. So subclasses of
            NetworkNode do not directly inherit from this class but rather from
            class *StoredNetworkNodeInfo* and this class has a reference to it
    """
    __storm_table__ = 'NetworkNode'
    id = storm.Int(primary=True)
    name = storm.Unicode()
    ip = storm.Unicode()
    info_type = storm.Int()
    x = storm.Int()
    y = storm.Int()
    _info = None

    def __init__(self, store, info_class, label, ip, x, y, **kwargs):
        """ Initializes Object

            Args:
                store (Storm.Store): Connection to database
                info_class (Class): Subclass of NetworkNode (e.g. PhysicalSwitch)
                name (String): Human readable name for the network node
                ip (String): IPv4 address of the node
                **kwargs (Arguments): Further arguments being passed to constructor
                    of subclass

            Example:
                During initialization constructor of *info_class* is called and
                **kwargs, additional name-value pairs for the subclass are passed.

                >>> controller = NetworkNode(
                ...     store=somestore,
                ...     info_class=Controller,
                ...     name='somename',
                ...     ip='someip',
                ...     location='Controller location',
                ...     ip_port=9000
                ...     )
        """
        super(NetworkNode, self).__init__()
        self.name = label
        self.ip = ip
        self.info_type = info_class.info_type
        self.x = x
        self.y = y
        store.add(self)
        store.flush()
        self._info = info_class(self, **kwargs)

    @property
    def info(self):
        """ Returns object of subclass

            Returns:
                Object
        """
        if self._info is not None:
            return self._info
        assert self.id is not None
        info_class = network_node_info_types[self.info_type]
        if not hasattr(info_class, '__storm_table__'):
            info = info_class.__new__(info_class)
            info.network_node = self
        else:
            info = storm.Store.of(self).get(info_class, self.id)
        self._info = info
        return info

    def to_dictionary(self):
        """ Returns class attributes of subclass and NetworkNode as dictionary

            Returns:
                Dictionary
        """
        dic = self.info.to_dictionary()
        dic['id'] = self.id
        dic['label'] = self.name
        dic['x'] = self.x
        dic['y'] = self.y
        if type(self.info) != Host:
            dic['ip'] = self.ip
        return dic


class NetworkNodeInfo(object):
    """ Base class for all classes inheriting from *NetworkNode* relation

        Attributes:
            network_node: Object being the parent NetworkNode object
    """
    def __init__(self, network_node):
        """ Initializes object

            Args:
                network_node (Object): *NetworkNode* object being parent of
        """
        self.network_node = network_node


class StoredNetworkNodeInfo(NetworkNodeInfo):
    """ Comes into action when retrieving/writing from database. Defines a
        reference between the relation of the subclass and the relation
        *NetworkNode*

        Attributes:
            network_node_id: Integer being primary key of both, *NetworkNode*
                relation and any relation inheriting from it
            network_node: Object being the parent of the subclass
    """
    network_node_id = storm.Int(primary=True)
    network_node = storm.Reference(network_node_id, NetworkNode.id)


class PhysicalSwitch(StoredNetworkNodeInfo):
    """ ORM for relation *PhysicalSwitch*.

        Schema *PhysicalSwitch* inherits from schema *NetworkNode*. However in
        Storm the *infoheritance* pattern is used utilizing wrappers. So this
        class extends class ``StoredNetworkNodeInfo`` and class ``NetworkNode``
        representing schema *NetworkNode* has an instance of class
        ``NetworkNodeInfo`` being in turn a superclass of ``StoredNetworkNodeInfo``.

        :ref:`infoheritance explanation <infoheritance_desc>`
        When programmatically creating an instance of ``PhysicalSwitch`` an
        instance of ``NetworkNode`` has to be created and ``PhysicalSwitch``
        passed as argument.
        When the object is then written to the database, Storm takes care of
        writing everything into the correct schema.
        **When creating a switch in your code you do not instanciate an object
        of this class!**

        In case a switch should be retrieved from the database, ``NetworkNode``
        is used along with the retrieval methods.
        Storm resolves the inheritance and returns a ``NetworkNode`` instance
        with the respective object of type ``PhysicalSwitch`` stored in ``_info``
        attribute. Note that even though a switch is fetched, type of returned
        object will be ``NetworkNode``.

        Example:
            >>> switch = NetworkNode(
            ...     store=somestore,
            ...     info_class=PhysicalSwitch,
            ...     name='cool_switch',
            ...     ip='192.168.178.2'
            ...     dpid='00:00:00:00:00:00:00:10',
            ...     cplane=False,
            ...     ip_port=9100,
            ...     num_ports=40
            ...     )
            >>> somestore.add(switch)
            >>> somestore.flush()
            >>> id = switch.id
            >>> somestore.commit()

        Example:
            >>> switch = somestore.get(NetworkNode, id)
            >>> print switch.ip
            192.168.178.2
            >>> print switch.info.name
            cool_switch
            >>> print switch.info.dpid
            00:00:00:00:00:00:00:10

        Attributes:
            __storm_table__: String defining relation class is mapping to
            dpid: String representing Data-Path-ID (MAC Address) of switch
            ip_port: Integer representing port switch is listening for controller
                connections
            num_ports: Integer specifying number of ports this switch has
            c_plane: Boolean specifying whether switch is in control or data plane
            model: Unicode specifying model of switch used to derive rate limit
    """

    __storm_table__ = 'PhysicalSwitch'
    network_node_id = storm.Int(primary=True)
    dpid = storm.Unicode()
    ip_port = storm.Int()
    num_ports = storm.Int()
    cplane = storm.Bool()
    model = storm.Unicode()

    ports = storm.ReferenceSet(network_node_id, PhysicalPort.switch_id)

    def __init__(self, network_node, dpid, cplane, model='lab_switch',
            ip_port=None, num_ports=None):
        """ Initializes Object. Called by constructor of ``NetworkNode``. Should
            never be called by user

            Args:
                network_node (data.dbinterfaces.NetworkNode): Object of "Parent
                    class"
                dpid (String): Data-Path-Id (MAC address)
                cplane (Boolean): Whether or not switch is located in control
                    plane
                ip_port (int, optional): Port switch is listening for controller
                    connections
                num_ports (int, optional): Number of ports the switch has

            Note:
                If ``ip_port`` is not specified, it defaults to 9000

            Note:
                If ``num_ports`` is not specified it defaults to 10
        """
        super(PhysicalSwitch, self).__init__(network_node)
        self.dpid = dpid
        self.cplane = cplane
        self.ip_port = ip_port
        self.num_ports = num_ports
        self.model = model

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                Dictionary
        """
        dic = {}
        dic['type'] = 'switch'
        dic['dpid'] = self.dpid
        dic['port'] = self.ip_port
        dic['num_ports'] = self.num_ports
        dic['cplane'] = self.cplane
        dic['model'] = self.model
        return dic


class Host(StoredNetworkNodeInfo):
    """ ORM class representing schema *Host*. Inherits (DB schema) from schema
        *NetworkNode*

        For detailed description of how inheritance in the databse schema works
        refer to :ref: `infoheritance_desc` in class ``PhysicalSwitch``

        Attributes:
            vsdn_id: Integer being foreign key to relation *Vsdn* Host belongs to
    """
    __storm_table__ = 'Host'
    vsdn_id = storm.Int()

#    vsdn = storm.Reference(vsdn_id, Vsdn.id)

    def __init__(self, network_node, vsdn_id):
        """ Initializes Object. Always called by ``NetworkNode``, should never
            be called by user

            Attributes:
                network_node (db.dbinterfaces.NetworkNode): Object of "parent
                    class"
                vsdn_id (int): Integer being foreign key to VSDN host belongs to
        """
        super(Host, self).__init__(network_node)
        self.vsdn_id = vsdn_id

    def to_dictionary(self):
        """ Return class attributes as dictionary

            Returns:
                dictionary
        """
        dic = {'type':'host'}
        return dic


class Controller(StoredNetworkNodeInfo):
    """ ORM class representing schema *Controller*. Inherits (DB schema) from
        schema *NetworkNode*

        For detailed description of how inheritance in the databse schema works
        refer to :ref: `infoheritance_desc` in class ``PhysicalSwitch``

        Attributes:
            __storm_table__: String specifying relation class is mapping to
            entry_point: Foreign key to Physical Switch serving as access
                point to control plane.
            ip_port: Integer specifying port Controller is listening on
    """
    __storm_table__ = 'Controller'
    entry_point = storm.Int()
    ip_port = storm.Int()

#    vsdn = storm.Reference(id, Vsdn.controller_id)

    def __init__(self, network_node, entry_point, ip_port=6633, **kwargs):
        """ Initializes Object. Always called by ``NetworkNode``, should never
            be called by user

            Attributes:
                network_node (db.dbinterfaces.NetworkNode): Object of "parent
                    class"
                entry_point (int): PhysicalSwitch id serving as entry point
                    to control network.
                ip_port (int, optional): Port controller is listening on

            Note:
                If ``ip_port`` is not specified it defaults to 9100
        """
        super(Controller, self).__init__(network_node)
        self.entry_point = entry_point
        self.ip_port = ip_port

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns
                dictionary
        """
        return {'entry_point':self.entry_point,
                'ip_port':self.ip_port,
                'type':'controller'
                }


class Hypervisor(StoredNetworkNodeInfo):
    """ ORM class representing schema *Hypervisor*. Inherits (DB schema) from
        schema *NetworkNode*

        For detailed description of how inheritance in the databse schema works
        refer to :ref: `infoheritance_desc` in class ``PhysicalSwitch``

        Attributes:
            __storm_table__: String specifying relation class is mapping to
            status: String specifying status of hypervisor (running, transition)
            user: String specifying user for hypervisor
            password: String specifying password for user for hypervisor
            port: Int specifying port to connect to hypervisor (mgmt)
            model: Unicode specifying model of hypervisor used to derive limits
            total_cpu: Double representing the total amount of CPU capacity
                (in percent) of the node
            used_cpu: Double representing allocated amount of CPU (in percent)
            cfg_msg_rate: Integer representing the sum of message rates
                defined for slices governed by hypervisor.
    """
    __storm_table__ = 'Hypervisor'
    status = storm.Int()
    user = storm.Unicode()
    password = storm.Unicode()
    port = storm.Int()
    model = storm.Unicode()
    total_cpu = storm.Float()
    used_cpu = storm.Float()
    cfg_msg_rate = storm.Int()

    def __init__(self, user, password, port, model=u'lab_pc', status=1,
            total_cpu=400, used_cpu=0, configured_message_rate=0):
        """ Initializes Object. Always called by ``NetworkNode``, should never
            be called by user

            Attributes:
                network_node (db.dbinterfaces.NetworkNode): Object of "parent
                    class"
                status (String, optional): Status of Hypervisor

            Note:
                If ``status`` not specified defaults to RUNNING
        """
        self.user = user
        self.password = password
        self.port = port
        self.status = status
        self.model = model
        self.total_cpu = total_cpu
        self.used_cpu = used_cpu
        self.configured_message_rate = configured_message_rate

    @property
    def num_cores(self):
        """ Calculates number of cores from to total amount of CPU
        """
        return self.total_cpu / 100

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                dictionary
        """
        return {
                'status': self.status,
                'type': 'hypervisor',
                'user': self.user,
                'password': self.password,
                'port': self.port,
                'model': self.model,
                'total_cpu': int(self.total_cpu / self.num_cores),
                'used_cpu': int(self.used_cpu / self.num_cores)
                }


class PhysicalEdge(IterMixin):
    """ ORM class representing schema PhysicalEdge

        Attributes:
            __storm_table__: String specifying relation, class is mapping to
            node_one_id: Integer being foreign key to relation *NetworkNode*
            node_two_id: Integer being foreign key to relation *NetworkNode*
            port_one_id: Integer being foreign key to relation *PhysicalPort*.
            port_two_id: Integer being foreign key to relation *PhysicalPort*
            port_one: Object of type ``PhysicalPort`` representing port of
                start/endpoint of edge (if start/end node is switch)
            port_two: Object of type ``PhysicalPort`` representing port of
                start/endpoint of edge (if start/end node is switch)
    """
    __storm_table__ = 'PhysicalEdge'
    id = storm.Int(primary=True)

    node_one_id = storm.Int()
    node_two_id = storm.Int()
    port_one_id = storm.Int()
    port_two_id = storm.Int()

    port_one = storm.Reference(port_one_id, PhysicalPort.id)
    """ This is an example of a one-to-one mapping. When ``PhysicalEdge`` object
        is created in context of a DB retrieval, Storm will resolve this reference
        and also load the respective entry from *PhysicalPort*
    """
    port_two = storm.Reference(port_two_id, PhysicalPort.id)

    def __init__(self, node_one_id, node_two_id, port_one_id=None, port_two_id=None):
        """ Initializes Object

            Args:
                node_one_id (int): Primary key of *NetworkNode edge starts/ends
                node_two_id (int): Primary key of *NetworkNode edge starts/ends
                port_one_id (int, optional): Primary key of *PhysicalPort* edge
                    starts/ends. Intended for switches/nodes with multiple ports
                port_two_id (int, optional): Primary key of *PhysicalPort* edge
                    starts/ends. Intended for switches/nodes with multiple ports
        """
        super(PhysicalEdge, self).__init__()
        self.node_one_id = node_one_id
        self.node_two_id = node_two_id
        self.port_one_id = port_one_id
        self.port_two_id = port_two_id

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                dictionary
        """
        print(self.id)
        dic =  {'from_node':self.node_one_id,
                'to_node':self.node_two_id,
                'id':self.id
                }
        if self.port_one_id is not None:
            dic['from_port'] = self.port_one.number
        if self.port_two_id is not None:
            dic['to_port'] = self.port_two.number
        return dic


class LogicalEdge(IterMixin):
    """ ORM mapping class to relation *LogicalEdge*

        Attributes:
            __storm_table__: String specifying relation class is refering to
            node_one_id: Integer being foreign key for relation *NetworkNode*
                specifying start/end point of logical link
            node_two_id: Integer being foreign key for relation *NetworkNode*
                specifying start/end point of logical link
            vsdn_id: Integer being foreing key for relation *Vsdn* specifying
                VSDN logical link belongs to
            node_one: Reference to the node specified by ``node_one_id``
            node_two: Reference to the node specified by ``node_two_id``
            physical_embedding: List of objects of type ``PhysicalEdge``
                representing the actual edges this logical edge is realized with
    """

    __storm_table__ = 'LogicalEdge'
    id = storm.Int(primary=True)
    node_one_id = storm.Int()
    node_two_id = storm.Int()
    vsdn_id = storm.Int()
    datarate = storm.Int()
    cplane = storm.Bool()

    node_one = storm.Reference(node_one_id, NetworkNode.id)
    node_two = storm.Reference(node_two_id, NetworkNode.id)
#    vsdn_id = storm.Reference(vsdn_id, Vsdn.id)

    physical_embedding = storm.ReferenceSet(
            id,
            LogicalEdgeEmbedding.logical_edge_id,
            LogicalEdgeEmbedding.physical_edge_id,
            PhysicalEdge.id
            )
    """ This is an example of a many-to-one relation. When ``LogicalEdge`` object
        is fetched from database, Storm will also fetch all records from
        PhysicalEdge this logical edge is implemented with.
    """

    def __init__(self, node_one_id, node_two_id, vsdn_id, datarate=None, cplane=False):
        """ Initializes object

            Args:
                node_one_id (int): Foreign key to relation *NetworkNode*
                node_two_id (int): Foreign key to relation *NetworkNode*
                vsdn_id (int): Foreign key to relation *Vsdn*
        """
        super(LogicalEdge, self).__init__()
        self.node_one_id = node_one_id
        self.node_two_id = node_two_id
        self.vsdn_id = vsdn_id
        self.datarate = datarate
        self.cplane = cplane

    @property
    def physical_nodes(self):
        """ Returns list of physical nodes *in the order they were added to
            the database*. That means first one is, were user started edge,
            last one is node where user ended.

            Returns:
                List of NetworkNodes
        """
        edges = [edge for edge in self.physical_embedding]
        tmp = [edges[1].node_one_id, edges[1].node_two_id]
        nodes = [edges[0].node_one_id]

        # Find node link is beginning at. Place that node as first element in
        # list, which id is not contained in subsequent edge
        if edges[0].node_two_id in tmp:
            nodes.append(edges[0].node_two_id)
        else:
            nodes.insert(0, edges[0].node_two_id)
        tmp = nodes
        for i in range(1, len(edges)):
            # Check if first node id has been element of previous edge. If not
            # add node id to list and continue, else add other node since
            # this must be the id of the next node
            if edges[i].node_one_id not in tmp:
                nodes.append(edges[i].node_one_id)
            else:
                nodes.append(edges[i].node_two_id)
            tmp = [edges[i].node_two_id, edges[i].node_one_id]

        return nodes

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                Dictionary
        """
        dic =  {'id':self.id,
                'from_node':self.node_one.id,
                'to_node':self.node_two.id,
                'vsdn_id':self.vsdn_id,
                'datarate':self.datarate,
                'cplane':self.cplane,
                'embedding': [switch.id for switch in self.physical_embedding]
                }
        return dic


class Vsdn(IterMixin):
    """ ORM class mapping to relation *Vsdn*

        Attributes:
            __storm_table__: String specifying relation class is mapping to
            id: Primary key of relation
            name: String being human readable name of VSDN
            tenant_id: Integer being foreign key to relation *Tenant*
            controller_id: Integer being foreign key to relation *NetworkNode*
                representing the controller controlling this VSDN
            color: String specifying a color in HEX-format with which the VSDN
                will be displayed in the GUI
            subnet: String specifying subnet mask defining IP-subnet for slice
            hypervisor_id: Integer being foreign key to relation *NetworkNode*
                referencing the Hypervisor responsible for this VSDN
            message_rate: Integer specifying the number of messages per second
                for this slice
            password: Unicode String, password of slice
            isolation: Integer, isolation method for slice (1=network,
                2=software)
            controller: NetworkNode object representing controller specified by
                ``controller_id``
            hypervisor: NetworkNode object representing hypervisor specified by
                ``hypervisor_id``
            _hosts: Set of ``Host`` objects being the Hosts belonging to
                this VSDN
            logical_edges: Set of ``LogocalEdge`` objects being logical edges
                defined for this VSDN
            switches: Set of ``PhysicalSwitch`` objects being the switches
                serving as physical topology for this VSDN
            limit: Object of type RateLimit storing isolation method and rate
                limit for slice.
            bitrate: Int describing the bitrate message rate requested for VSDN
                corresponds to given the access switch.
            cpu_usage: Double describing the CPU usage the requested messsage
                rate for VSDN is corresponding to given a specific hypervisor
                node and previous requests.
    """
    __storm_table__ = 'Vsdn'
    id = storm.Int(primary=True)
    name = storm.Unicode()
    tenant_id = storm.Int()
    controller_id = storm.Int()
    color = storm.Unicode()
    subnet = storm.Unicode()
    hypervisor_id = storm.Int()
    message_rate = storm.Int()
    isolation = storm.Int()
    password = storm.Unicode()
    allocated_cpu = storm.Float()
    bitrate = storm.Int()

    controller = storm.Reference(controller_id, NetworkNode.id)
    hypervisor = storm.Reference(hypervisor_id, NetworkNode.id)
#    tenant = storm.Reference(tenant_id, Tenant.id)

    _hosts = storm.ReferenceSet(id, Host.vsdn_id)
    logical_edges = storm.ReferenceSet(id, LogicalEdge.vsdn_id)

    switches = storm.ReferenceSet(
            id,
            SwitchToVsdn.vsdn_id,
            SwitchToVsdn.switch_id,
            NetworkNode.id
            )

    def __init__(self, name, tenant_id, controller_id, hypervisor_id,
            message_rate, password, isolation=2, color=None, subnet=None):
        """ Initializes object

            Args:
                name (String): Name of the VSDN
                tenant_id (int): Foreign key to relation *Tenant*
                controller_id (int): Foreign key to relation *NetworkNode*
                hypervisor_id (int): Foreign key to relation *NetworkNode*
                color (String, optional): HEX-format color
                subnet (String, optional): IPv4-subnet mask
        """
        super(Vsdn, self).__init__()
        self.name = name
        self.tenant_id = tenant_id
        self.controller_id = controller_id
        self.hypervisor_id = hypervisor_id
        self.message_rate = message_rate
        self.isolation_method = isolation
        self.password = password
        self.isolation_method = isolation
        self.allocated_cpu = 0
        self.bitrate = 0

        if color is not None:
            self.color = color
        if subnet is not None:
            self.subnet = subnet

    @property
    def isolation_method(self):
        """ Returns value of attribute ``isolation``.

            Returns:
                isolation: Integer representing isolation, 1 corresponds to
                    software, 2 to hardware isolation
        """
        return self.isolation

    @isolation_method.setter
    def isolation_method(self, isolation):
        """  Sets value of isolation attribute.

            Args:
                isolation (string, int): Type of isolation, will be stored as
                    int. Possible values are 'nw' --> 2, 'sw' --> 1
        """
        if type(isolation) == str:
            if isolation == 'sw':
                self.isolation = 1
            if isolation == 'nw':
                self.isolation = 2
        elif 1 <= isolation <= 2:
            self.isolation = isolation
        else:
            raise AttributeError(
                'Undefined value {} for attribute Vsdn.isloation_method'.format(
                    isolation
                    )
                )

    def get_hosts(self, store):
        """ Returns the Hosts belonging to this VSDN

            The Objects in ``_hosts`` are actually of type ``Host``. All
            information stored in relation ``NetworkNode`` is missing.
            Therefore this method fetches the entries from *NetworkNode* and
            returns a set of ``NetworkNode`` objects.

            Args:
                store (Storm.Store): Connection to database
        """
        return store.find(
                NetworkNode,
                [NetworkNode.info_type == int(data_config['host_info_type'])]
                )

    def set_attributes(self, attributes):
        """ Sets multiple attributes at once

            Args:
                attributes (dic): Dictionary, key names must be the same as
                    attribute names
        """
        if 'color' in attributes.keys():
            self.color = attributes.pop('color')
        if 'message_rate' in attributes.keys():
            self.message_rate = int(attributes.pop('message_rate'))
        if 'isolation_method' in attributes.keys():
            self.isolation_method = attributes.pop('isolation_method')

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                dictionary
        """
        return {'id':self.id,
                'name':self.name,
                'color':self.color,
                'message_rate': self.message_rate,
                'isolation_method': self.isolation_method,
                'password':self.password,
                'controller_url': '{}:{}'.format(
                    self.controller.ip,
                    self.controller.info.ip_port
                    ),
                'subnet': self.subnet,
                'allocated_cpu': self.allocated_cpu,
                'bitrate': self.bitrate
                }


class User(IterMixin):
    """ ORM class referencing to relation *User*

        Attributes:
            __storm_table__: String specifying relation class is mapping to
            id: Integer being primary key of relation
            name: String being name of tenant
            vsdns: List of ``Vsdn`` objects representing VSDNs belonging to tenant
    """
    __storm_table__ = 'User'
    id = storm.Int(primary=True)
    name = storm.Unicode()
    password = storm.Unicode()
    role = storm.Unicode()

    vsdns = storm.ReferenceSet(id, Vsdn.tenant_id)

    def __init__(self, name, password, role):
        """ Initializes Object

            Args:
                name (String): Name of user
                password (String): Password of user
                role (String): Role of user
        """
        super(User, self).__init__()
        self.name = name
        self.password = password
        self.role = role

    def to_dictionary(self):
        """ Returns class attributes as dictionary

            Returns:
                Dictionary
        """
        return {'id':self.id,
                'name':self.name
                }


class FlowVisorFlowMatch(IterMixin):
    """ ORM class Referencing relation *FlowVisorFlowMatch*.
        Represents a flow match structure

        Attributes:
            id (storm.Int): primary key
            in_port (Storm.Int): Matches physical port_no.  Switch ports are
                numbered as displayed by fvctl list-datapath-info DPID.
            dl_vlan (Storm.Unicode): Matches IEEE 802.1q virtual LAN tag vlan.
                Specify 0xffff as vlan to match packets that are not tagged with
                a virtual LAN; otherwise, specify a number between 0 and 4095,
                inclusive, as the 12-bit VLAN ID to match.
            dl_src (Storm.Unicode): Matches Ethernet source address mac, which
                should be specified as 6 pairs of hexadecimal digits delimited
                by colons, e.g. 00:0A:E4:25:6B:B0.
            dl_dst (Storm.Unicode): Matches Ethernet destination address mac.
            dl_type (Storm.Unicode): Matches Ethernet protocol type ethertype,
                which should be specified as a integer between 0 and 65535,
                inclusive, either in decimal or as a hexadecimal number
                prefixed by 0x, e.g. 0x0806 to match ARP packets
            nw_src (Storm.Unicode): Matches IPv4 source address ip, which
                should be specified as an IP address, e.g. 192.168.1.1. The
                optional netmask allows matching only on an IPv4 addressprefix.
                The netmask is specified "CIDR-style", i.e., 192.168.1.0/24.
            nw_dst (Storm.Unicode): Matches IPv4 destination address ip.
            nw_proto (Storm.Unicode): Matches IP protocol type proto, which
                should be specified as a decimal number between 0 and 255,
                inclusive, e.g. 6 to match TCP packets.
            nw_tos (Storm.Unicode): Matches ToS/DSCP (only 6-bits, not modify
                reserved 2-bits for future use) field of IPv4 header tos/dscp,
                which should be specified as a decimal number between 0 and 255,
                inclusive.
            tp_src (Storm.Unicode): Matches transport-layer (e.g., TCP, UDP,
                ICMP) source port, which should be specified as a decimal number
                between 0 and 65535 (in the case of TCP or UDP) or between 0 and
                255 (in the case of ICMP), inclusive, e.g. 80 to match packets
                originating from a HTTP server.
            tp_dst (Storm.Unicode): Matches transport-layer destination port.
    """
    __storm_table__ = 'FlowVisorFlowMatch'
    id = storm.Int(primary=True)
    in_port = storm.Int()
    dl_vlan = storm.Unicode()
    dl_src = storm.Unicode()
    dl_dst = storm.Unicode()
    dl_type = storm.Unicode()
    nw_src = storm.Unicode()
    nw_dst = storm.Unicode()
    nw_proto = storm.Unicode()
    nw_tos = storm.Unicode()
    tp_src = storm.Unicode()
    tp_dst = storm.Unicode()

    def __init__(self, in_port=None, dl_vlan=None, dl_src=None, dl_dst=None,
            dl_type=None, nw_src=None, nw_dst=None, nw_proto=None, nw_tos=None,
            tp_src=None, tp_dst=None):
        super(FlowVisorFlowMatch, self).__init__()
        self.in_port = in_port
        self.dl_vlan = dl_vlan
        self.dl_src = dl_src
        self.dl_dst = dl_dst
        self.dl_type = dl_type
        self.nw_src = nw_src
        self.nw_dst = nw_dst
        self.nw_proto = nw_proto
        self.nw_tos = nw_tos
        self.tp_src = tp_src
        self.tp_dst = tp_dst

    def to_dictionary(self):
        dic = {
                'id': self.id,
                'in_port': self.in_port,
                'dl_vlan': self.dl_vlan,
                'dl_src': self.dl_src,
                'dl_dst': self.dl_dst,
                'dl_type': self.dl_type,
                'nw_src': self.nw_src,
                'nw_dst': self.nw_dst,
                'nw_proto': self.nw_proto,
                'nw_tos': self.nw_tos,
                'tp_src': self.tp_src,
                'tp_dst': self.tp_dst
            }
        return dic

    def to_cmd(self):
        cmd = ''
        for key, value in self.to_dictionary().iteritems():
            logging.debug(value)
            if value is not None:
                cmd += '{}={},'.format(key, value)
        return cmd[:-1]


class SlicePermission(IterMixin):
    """ ORM class referencing relation *SlicePermission*

        Attributes:
            id (storm.Int): Primary key
            flow_visor_flow_space_id (storm.Int): Foreign key to
                *FlowVisorFlowSpace* relation
            vsdn_id (storm.Int): Foreign key to *Vsdn* relation
            permission (storm.Int): Permission VSDN with ``vsdn_id`` has
                on flowspace

        Possible Values for ``permission``:
            1: Delegate
            2: Read
            4: Write
            3: Delegate, Read
            7: Full
            6: Read, Write
            5: Delegate, Write
    """

    __storm_table__ = 'SlicePermission'
    id = storm.Int(primary=True)
    flow_visor_flow_space_id = storm.Int()
    vsdn_id = storm.Int()
    permission = storm.Int()

    vsdn = storm.Reference(vsdn_id, Vsdn.id)

    def __init__(self, fvfsid, vsdn_id, permission):
        """ Initializes object

            Raises:
                AssertionError if 1 < permission > 7
        """
        super(SlicePermission, self).__init__()
        assert permission > 0 and permission < 8, 'Undefined permission {}'.format(permission)
        self.flow_visor_flow_space_id = fvfsid
        self.vsdn_id = vsdn_id
        self.permission = permission

    def to_dictionary(self):
        dic = {
                'id': self.id,
                'flow_visor_flow_space_id': self.flow_visor_flow_space_id,
                'vsdn_id': self.vsdn_id,
                'permission': self.permission,
                }
        return dic

    @property
    def slice_name(self):
        """ Returns name of associated slice

            Returns:
                String
        """
        return self.vsdn.name


class FlowVisorFlowSpace(IterMixin):
    """ ORM class referencing relation *FlowVisorFlowSpace*

        Attributes:
            id (storm.Int): Primary Key
            name (storm.Unicode): Name of FlowSpace
            dpid (storm.Unicode): MAC address of switch flow-space is intended
            flowmatch_id (storm.Int): Foreign key to relation
                *FlowVisorFlowMatch* specifying on what to slice
    """
    __storm_table__ = 'FlowVisorFlowSpace'
    id = storm.Int(primary=True)
    name = storm.Unicode()
    dpid = storm.Unicode()
    flowmatch_id = storm.Int()
    priority = storm.Int()

    flowmatch = storm.Reference(flowmatch_id, FlowVisorFlowMatch.id)
    slice_permissions = storm.ReferenceSet(id, SlicePermission.flow_visor_flow_space_id)

    def __init__(self, name, dpid, flowmatch_id, priority):
        """ Initializes object
        """
        self.name = name
        self.dpid = dpid
        self.flowmatch_id = flowmatch_id
        self.priority = priority

    def to_dictionary(self):
        dic = {
                'id': self.id,
                'name': self.name,
                'dpid': self.dpid,
                'flowmatch_id': self.flowmatch_id,
                'priority': self.priority
                }
        return dic

    def get_slice_permission(self, vsdn_id):
        """ Returns slice perissions of vsdn specified by argument ``vsdn_id``
            or none if no permission is found.

            Args:
                vsdn_id (int): Primary Key of vsdn

            Returns:
                data.dbinterfaces.SlicePermission
        """
        ret = None
        for permission in self.slice_permissions:
            if permission.vsdn_id == vsdn_id:
                ret = permission
                break
        return ret

    def to_request(self):
        """ Returns dictionary as expected by management api.

            Implemented here because it is a class tailored specifically to
            FlowVisor anyway and else would clutter ``hypervisor`` module

            Args:
                vsdn_id (int): Primary key for VSDN for which slice permission
                    should be used

            Returns:
                Dictionary
        """
        match = self.flowmatch.to_dictionary()
        match.pop('id')
        keys = list(match.keys())
        for key in keys:
            if match[key] is None:
                match.pop(key)

        actions = []
        for perm in self.slice_permissions:
            actions.append({
                'slice_name': perm.slice_name,
                'permission': perm.permission
                })

        space = self.to_dictionary()
        space.pop('id')
        space.pop('flowmatch_id')
        space['match'] = match
        space['slice_action'] = actions

        return space


class RegressionModel(IterMixin):
    """ ORM class referencing relation *RegressionModel* defining (polynomial)
        regression models for properties of devices
    """
    __storm_table__ = 'RegressionModel'
    id = storm.Int(primary=True)
    key = storm.Unicode()
    regression_model = storm.Unicode()

    def __init__(self, key, model):
        """ Initializes object

            Args:
                key (unicode): String representing specific device for which to
                    store a regression model.
                model (Unicode): Pickled representation of a sclearn.model
        """
        self.key = key
        self.regression_model = model


class StormConnector(object):
    """ This class establishes the connection to the database using Storm. It does
        also define sql queries going over a simple get/set.

        Attributes:
            config: Dictionary specifying default settings and configuration
                settings
            connection: Connection to database
            store: Representation of database
    """

    def __init__(self):
        """ Initializes Object
        """
        self._config = data_config
        self._logger = logging.getLogger('StormConnector')
        self._connection = storm.create_database(
                'mysql://{uname}:{pwd}@{host}:{port}/{schema}'.format(
                    uname = self._config['user'],
                    pwd = self._config['password'],
                    host = self._config['ip'],
                    port = self._config['port'],
                    schema = self._config['schema_name']
                    )
                )
        print ' user:'+self._config['user']+' pwd: '+self._config['password']+' ip: '+str(self._config['ip'])+' port: '+str(self._config['port'])+' schema '+ self._config['schema_name']

        self._store = storm.Store(self._connection)
        if int(self._config['host_info_type']) not in network_node_info_types.keys():
            register_network_node_info_type(
                    int(self._config['host_info_type']),
                    Host
                    )
        if int(self._config['switch_info_type']) not in network_node_info_types.keys():
            register_network_node_info_type(
                    int(self._config['switch_info_type']),
                    PhysicalSwitch
                    )
        if int(self._config['controller_info_type']) not in network_node_info_types.keys():
            register_network_node_info_type(
                    int(self._config['controller_info_type']),
                    Controller
                    )
        if 4 not in network_node_info_types:
            register_network_node_info_type(4, Hypervisor)

    def __del__(self):
        """ When object is destroyed clean up ressources
        """
        self._store.close()

    @property
    def store(self):
        """ Returns store object of connector

            Returns:
                Storm.Store
        """
        return self._store

    def _is_network_node_subclass(self, cls):
        """ Determines whether given class is subclass of NetworkNode.

            Args:
                cls (class): class which should be determined

            Returns:
                is_subclass: True if subclass else false
        """
        name = str(cls)
        index = name.rfind('.')
        name = name[index + 1:-2]

        is_network_node = False

        for c in network_node_info_types.itervalues():
            stringified = str(c)
            index = stringified.rfind('.')
            if name == stringified[index + 1:-2]:
                is_network_node = True
                cls = c
                break
        return is_network_node

    def get_network_nodes(self, info_classes=None):
        """ Returns network nodes of a specific info class

            Args:
                info_class (Class): Any class inheriting from StoredNetworkNodeInfo
                    and registered
        """
        where = []
        if info_classes is not None:
            info_types = [info_class.info_type for info_class in info_classes]
            where = [NetworkNode.info_type.is_in(info_types)]
        result = self._store.find(NetworkNode, *where)
        result.order_by(NetworkNode.name)
        return result

    def get_object(self, cls, id):
        """ Returns object of type ``cls``.

            Args:
                cls (classname): Any ORM class
                id (int): Id of object
        """
        if self._is_network_node_subclass(cls):
            element = self.store.find(
                    NetworkNode,
                    [NetworkNode.info_type == int(cls.info_type), NetworkNode.id == id]
                    ).one()
        else:
            element = self.store.get(cls, id)
        return element

    def get_objects(self, cls, where=[]):
        """ Searches databse of a set of objects with given restrictions.
            Restrictions are and combined.

            Args:
                cls (class): Class which should be retrieved
                where (list): List of restrictions

            Returns:
                objects: ordered storm.ResultSet after ID
        """
        objects = None
        if self._is_network_node_subclass(cls):
            origin = [
                    NetworkNode,
                    storm.Join(
                        cls,
                        NetworkNode.id == cls.network_node_id
                        )
                    ]
            where.append(NetworkNode.info_type == int(cls.info_type))
            objects = self.store.using(*origin).find(
                    NetworkNode,
                    *where
                    ).order_by(NetworkNode.id)
        else:
            objects = self.store.find(
                    cls,
                    *where
                    ).order_by(cls.id)
        return objects

    def get_physical_switches(self, switch_ids):
        """ Returns physical switches to given ids

            Args:
                switch_ids (list): List of primary keys

            Returns:
                storm.ResultSet
        """
        where = [
                NetworkNode.id in switch_ids,
                NetworkNode.info_type.is_in([PhysicalSwitch])
                ]
        result = self._store.find(NetworkNode, *where)
        result.order_by(NetworkNode.id)
        return result

    def get_vsdn(self, vsdn_id):
        """ Returns VSDN object or Iterator over VSDN objects depending on
            ``vsdn_id`` and ``tenant_id``.

            Args:
                vsdn_id (int): Primary key of VSDN
                tenant_id (int): Primary key of tenant

            Note:
                If ``vsdn_id`` is set method tries to retrieve this VSDN only.
                If ``vsdn_id`` is not set and ``tenant_id`` is set, all VSDN
                belonging to this tenant are returned.
                If neither is set all VSDNs there are are returned (For development
                purposes, will be removed)
        """
        return self.store.get(Vsdn, vsdn_id)

    def get_vsdns_of_tenant(self, tenant_id):
        self._logger.debug('get vsdns for tenant {}'.format(tenant_id))
        tenant = self.store.get(User, tenant_id)
        self._logger.debug('Number of vsdns: {}'.format(tenant.vsdns.count()))
        return tenant.vsdns

    def get_all_vsdns(self):
        """ Retrieves all VSDNs from the databse

            Returns:
                Ordered storm.ResultSet
        """
        vsdns = self.store.find(Vsdn, Vsdn.id > 0).order_by(Vsdn.id)
        return vsdns

    def get_physical_edge(self, node_one_id, node_two_id=None):
        """ Returns Edge between nodes

            Args:
                node_one_id (int): Primary key of node one
                node_two_id (int, optional): Primary key of other endpoint.

            Note:
                If node is a host/controller etc. it has only one physical
                connection. Therefore the second node id can be ommitted.

            Returns:
                PhysicalEdge
        """
        def generate_and(id_one, id_two):
            if id_one is None:
                return storm.And(id_two == PhysicalEdge.node_two_id)
            elif id_two is None:
                return storm.And(id_one == PhysicalEdge.node_one_id)
            else:
                return storm.And(
                    id_one == PhysicalEdge.node_one_id,
                    id_two == PhysicalEdge.node_two_id
                    )

        result = self.store.find(
                PhysicalEdge,
                generate_and(node_one_id, node_two_id)
                )
        if result.count() == 0:
            result = self.store.find(
                    PhysicalEdge,
                    generate_and(node_two_id, node_one_id)
                    )
        if result.count() == 0:
            raise RuntimeError('Could not find edge to ids {} and {}'.format(
                node_one_id, node_two_id))
        elif result.count() > 1:
            raise RuntimeError('Found more than one physical edge between ' + \
                    'nodes {} and {}'.format(node_one_id, node_two_id))
        return result.any()

    def get_logical_edges(self, node_one_id, node_two_id=None):
        """ Returns Edge between nodes

            Args:
                node_one_id (int): Primary key of node one
                node_two_id (int, optional): Primary key of other endpoint.

            Returns:
                LogicalEdge
        """
        def generate_and(id_one, id_two):
            if id_one is None:
                return storm.And(id_two == LogicalEdge.node_two_id)
            elif id_two is None:
                return storm.And(id_one == LogicalEdge.node_one_id)
            else:
                return storm.And(
                    id_one == LogicalEdge.node_one_id,
                    id_two == LogicalEdge.node_two_id
                    )

        result = self.store.find(
                LogicalEdge,
                generate_and(node_one_id, node_two_id)
                )
        if result.count() == 0:
            result = self.store.find(
                    LogicalEdge,
                    generate_and(node_two_id, node_one_id)
                    )
        if result.count() == 0:
            raise RuntimeError('Could not find edge to ids {} and {}'.format(
                node_one_id, node_two_id))
        elif result.count() > 1:
            for r in result:
                self._logger.debug(r.to_dictionary())
            raise RuntimeError('Found more than one physical edge between ' + \
                    'nodes {} and {}'.format(node_one_id, node_two_id))
        return result.order_by(LogicalEdge.id)

    def get_physical_topo(self,  vsdn_id=None, cplane=False):
        """ Returns physical topology (for an VSDN), that is all switches and
            edges between them

            Args:
                vsdn_id (int, optional): Primary key to relation *Vsdn* if set
                    only switches allocated to this VSDN and edges between them
                    are returned

            Returns:
                switches: List of ``NetworkNode`` objects with info type of
                    ``PhysicalSwitch``
                edges: List of ``PhysicalEdge`` objects
        """
        where = [PhysicalSwitch.cplane == cplane]
        edges = []
        switches = self.get_objects(PhysicalSwitch, where)
        sw_ids = [node.id for node in switches]
        where = [PhysicalEdge.node_one_id.is_in(sw_ids)]
        result = self.store.find(PhysicalEdge,*where)

        for edge in result:
            if edge.node_two_id in sw_ids:
                edges.append(edge)

        return (switches, edges)

    def get_flow_visor_flow_space(self, vsdn_id=None, where=[]):
        """ Returns flowvisor flowspace objects. If ``vsdn_id`` is ``None``
            all flowspace entries in database are returned

            Args:
                vsdn_id (int, optional): ID of VSDN for which flowspace should
                be returned

            Returns:
                spaces: storm.OrderedResultSet
        """
        spaces = None
        where.append(FlowVisorFlowSpace.id > -1)
        if vsdn_id is None:
            spaces = self.store.find(
                    FlowVisorFlowSpace,
                    *where
                    )
        else:
            where.append(FlowVisorFlowSpace.id == SlicePermission.flow_visor_flow_space_id)
            origin = [
                    FlowVisorFlowSpace,
                    storm.Join(SlicePermission, SlicePermission.vsdn_id == vsdn_id)
                    ]
            spaces = self.store.using(*origin).find(
                    FlowVisorFlowSpace,
                    *where
                    )
        return spaces

    def get_missing_dpids(self, vsdn_id, given_sw_ids):
        """ For given vsdn_id and switch_ids returns those switches, which do not
            yet occurre in any FlowVisorFlowSpace.

            Args:
                vsdn_id (int): Primary Key
                given_sw_ids (List): List PhysicalSwitch primary keys

            Returns:
                Storm.ResultSet
        """
        # Retrieves network_node_ids of all physical switches for which
        # flow spaces exist in the database.
        # So on the switches reprsented by subselect, slicing based on ip subnet
        # for the given vsdn is already implemented.
        subselect = storm.Select(
                PhysicalSwitch.network_node_id,
                storm.And(
                    PhysicalSwitch.dpid.like(FlowVisorFlowSpace.dpid),
                    FlowVisorFlowSpace.id == SlicePermission.flow_visor_flow_space_id,
                    SlicePermission.vsdn_id == vsdn_id
                    )
                )

        # Find those ids, for which no flow space is yet defined.
        #   - They must not be in subselect (for those flowspaces already exist)
        #   - They must be physical switches
        #   - They must be in the set of given switches
        result = self.store.find(
                NetworkNode,
                storm.And(
                    storm.Not(NetworkNode.id.is_in(subselect)),
                    NetworkNode.info_type == PhysicalSwitch.info_type,
                    NetworkNode.id.is_in(given_sw_ids)
                    )
                )
        # result is the intersection of physical switches with given switches
        # without those switches for which for given VSDN flowspaces are already
        # defined
        return result

    def get_hypervisor(self):
        """ Returns all hypervisor stored in database

            Returns:
                hypervisor: List of ``NetworkNode`` objects with info class
                    ``Hypervisor``
        """
        hypervisor = self._store.find(
                NetworkNode,
                NetworkNode.info_type == 4
                )
        return hypervisor

    def get_regression_model(self, device):
        """ Given the specification of a device returns an regression model
            approximating a property.

            Args:
                device (string):

            Returns:
                scikit_model: scikit_learn.model representing pretrained
                    (polynomial) regression model for some property
        """
        models = self.store.find(RegressionModel, RegressionModel.key == device)
        model = models.one()
        scikit_model = pkl.loads(str(model.regression_model))
        return scikit_model

    def get_switching_edges(self, switch_ids):
        """ Returns all physcial edges between specified switches.

            Args:
                switch_ids (List): List of integers being primary keys

            Returns:
                storm.ResultSet
        """
        set = self._store.find(
                PhysicalEdge,
                storm.And(
                    PhysicalEdge.node_one_id.is_in(switch_ids),
                    PhysicalEdge.node_two_id.is_in(switch_ids)
                )
            )
        return set

    def get_edges_by_node(self, node_id):
        """ Return all edges terminating or oriniating at the node with the
            given id

            Args:
                node_ids (int): Primary key to relation *NetworkNode*

            Returns:
                set: List of ``PhysicalEdge`` objects
        """
        set = self._store.find(
                PhysicalEdge,
                storm.Or(
                    PhysicalEdge.node_one_id == node_id,
                    PhysicalEdge.node_two_id == node_id
                )
            )
        return set

    def add_physical_switch(self, dictionary, vsdn_ids=None):
        """ Adds physical switch to the database and also creates entries for
            the ports of the switch

            Args:
                dictinary (Dictionary): Contains attributes of switch

            Returns:
                switch_id: Integer being primary key of newly added switch
        """
        #TODO: remove vsdn_ids
        for id in vsdn_ids:
            assert type(id) is int, ('VSDN primary key not an integer: ' +
                    '{}'.format(id)
                    )
        random.seed(time.time())
        if 'ip' not in dictionary:
            dictionary['ip'] = u'192.168.178.{}'.format(random.randrange(0, 254))
        if 'dpid' not in dictionary:
            dictionary['dpid'] = u'00:00:00:00:00:00:00:{:02d}'.format(
                    random.randrange(0, 99)
                    )
        if 'cplane' not in dictionary:
            dictionary['cplane'] = False
        if 'ip_port' not in dictionary:
            dictionary['ip_port'] = 9100
        if 'num_ports' not in dictionary:
            dictionary['num_ports'] = 10

        switch = NetworkNode(
                store=self.store,
                info_class=PhysicalSwitch,
                name=dictionary['label'],
                ip=dictionary['ip'],
                dpid=dictionary['dpid'],
                cplane=dictionary['cplane'],
                ip_port=dictionary['ip_port'],
                num_ports=dictionary['num_ports']
                )
        switch.x = dictionary['x']
        switch.y = dictionary['y']
        self.store.add(switch)
        self.store.flush()
        return switch.id

    def add_physical_port(self, dictionary):
        """ Writes a new physical port to the database

            Args:
                dictionary (Dictionary): Key-value pair of attributes of port
        """
        assert 'switch_id' in dictionary, 'Switch Id missing. Port not added'
        assert 'number' in dictionary, 'Port number missing. Port not added'
        assert 'speed' in dictionary, 'Speed missing, Port not added'

        port = PhysicalPort(
                switch_id=dictionary['switch_id'],
                number=dictionary['number'],
                speed=dictionary['speed']
                )
        self.store.add(port)
        self.store.flush()

    def add_controller(self, dictionary, vsdn_id):
        """ Writes a new controller to the databse and updates (overwrites)
            the controller set in *Vsdn* relation

            Args:
                dictionary (Dictionary): Key-Value pairs of attributes of
                    controller
                vsdn_id (int): Primary key of relation *Vsdn* Controller reigns
                    over

            Returns:
                id of new controller

            Raises:
                AscertionError: When ``vsdn_id`` is not integer
        """
        assert type(vsdn_id) is int, 'VSDN primary key not an integer: {}'.format(vsdn_id)
        self._logger.debug(dictionary)
        ctrl = NetworkNode(store=self.store, info_class=Controller, **dictionary)
        self.store.add(ctrl)
        self.store.flush()
        self.get_object(Vsdn, vsdn_id).controller_id = ctrl.id
        return ctrl.id

    def add_host(self, dictionary, vsdn_id):
        """ Writes a new host to the database.

            Args:
                dictionary (Dictionary): Key-Value pairs of attributes of Host
                vsdn_id (int): Primary key to *Vsdn* relation
        """
        assert type(vsdn_id) is int, 'VSDN primary key not an integer: {}'.format(vsdn_id)
        # def __init__(self, info_class, name, ip, vsdn_id):

        if 'label' not in dictionary:
            random.seed(time.time())
            dictionary['label'] = u'h{}'.format(random.randrange(0,1000))

        if 'ip' not in dictionary:
            dictionary['ip'] = u'192.168.178.{}'.format(random.randrange(0,254))

        host = NetworkNode(
                store=self.store,
                info_class = Host,
                name = dictionary['label'],
                ip = dictionary['ip'],
                vsdn_id = vsdn_id
                )
        self.store.add(host)

    def add_server(self, dictionary, vsdn_id):
        pass

    def add_switch_to_vsdn(self, switch_id, vsdn_id):
        record = SwitchToVsdn(switch_id, vsdn_id)

        self.store.add(record)

    def add_physical_edge(self, dictionary):
        pass

    def add_logical_edge(self, dictionary, vsdn_id):
        """ Writes a new logical link to the database (writing embedding happens
            separately)

            Args:
                dictionary (Dictionary): Key-Value pairs of attributes
                vsdn_id (int): Primary key to relation *Vsdn*
        """
        le = LogicalEdge(
                node_one_id=dictionary['to_node'],
                node_two_id=dictionary['from_node'],
                vsdn_id=vsdn_id,
                datarate=dictionary['datarate'] if 'datarate' in dictionary else None,
                cplane=dictionary['cplane'] if 'cplane' in dictionary else False,
                )

        self.store.add(le)
        self.store.flush()
        return le.id

    def add_logical_link_embedding(self, logical_edge_id, physical_edge_ids):
        """ Writes logical link embedding to database

            Args:
                logical_edge_id (int): Primary key of logical edge going to
                    be embedded
                physical_edge_ids (List): List of primary keys for switches
                    constituting logical edge
        """
        for physical in physical_edge_ids:
            self.store.add(LogicalEdgeEmbedding(logical_edge_id, physical))
        self.store.flush()

    def add_vsdn(self, dictionary):
        self._logger.debug(dictionary)
        vsdn = Vsdn(
                name=dictionary['name'],
                tenant_id=dictionary['tenant_id'],
                controller_id=None,
                hypervisor_id=dictionary['hypervisor_id'],
                color=dictionary['color'],
                subnet=dictionary['subnet'],
                isolation=int(dictionary['isolation_method']),
                message_rate=int(dictionary['message_rate']),
                password=dictionary['password'] if 'password' in dictionary.keys() else u'pwd'
                )
        self.store.add(vsdn)
        self.store.flush()
        return vsdn.id

    def add_flow_visor_flow_match(self, args):
        """ Adds new flow match to database.

            Args:
                args (Dictionary): Same keywords as for FlowMatch constructor
        """
        match = FlowVisorFlowMatch(**args)
        self.store.add(match)
        self.store.flush()
        return match.id

    def add_flow_visor_flow_space(self, name, dpid, flowmatch_id, priority=100):
        """ Adds new flow space to database

            Args:
                name (String): Name of flowspace
                dpid (String): Datapath id
                flowmatch_id (int): Primary key table FlowVisorFlowMatch
                priority (int, optional): Priority of flow space

            Returns:
                int, primary key of new flow space
        """
        space = FlowVisorFlowSpace(
                name=name,
                dpid=dpid,
                flowmatch_id=flowmatch_id,
                priority=priority
                )
        self.store.add(space)
        self.store.flush()
        return space.id

    def add_slice_permission(self, fvfs_id, vsdn_id, permission=7):
        """ Adds new slice permission to database

            Args:
                fvfs_id (int): FlowVisorFlowSpace id, primary key
                vsdn_id (int): Primary key
                permission (int, optional): permission of slice. Possible values:
                    1, 2, 4 and any sum of those values

            Returns:
                int, primary key
        """
        permission = SlicePermission(
                fvfsid=fvfs_id,
                vsdn_id=vsdn_id,
                permission=7
                )
        self.store.add(permission)
        self.store.flush()
        return permission.id

    def remove_controller(self, controller_id, vsdn_id):
        """  Removes controller instance from database and also deletes entry
            from *Vsdn* relation.

            Args:
                conroller_id (int): Primary key to *NetworkNode* relation
                vsdn_id (int): Primary key to *Vsdn* relation

            Raises:
                AssertionError: ``controller_id`` or ``vsdn_id`` not integer
        """
        try:
            controller = self.store.get(NetworkNode, controller_id)
            self.store.find(Vsdn, Vsdn.id == vsdn_id).set(controller_id=None)
            self.store.remove(controller)
            ctrl = self.store.get(Controller, controller_id)
            if ctrl is not None:
                self.store.remove(ctrl)
        except Exception as e:
            self.store.rollback()
            raise RuntimeError(
                    'Error in dbinterfaces.StromConnector.remove_controller ' +
                    'during removal of controller with id {} ' +
                    'Error was: "{}"'.format(controller_id, e.message)
                    )

    def remove_host(self, host_id):
        """ Removes host from database

            Args:
                host_id (int): Primary Key to relation *NetworkNode*

            Raises:
                AssertionError: ``host_id`` not an integer
        """
        try:
            host = self.store.get(NetworkNode, host_id)
            self.store.remove(host)
            host = self.store.get(Host, host_id)
            if host is not None:
                self.store.remove(host)

        except Exception as e:
            raise RuntimeError(
                    'Error in dbinterfaces.StormConnector.remove_host ' +
                    'during removal of host with id {} ' +
                    'Error was "{}"'.format(host_id, e.message)
                    )

    def remove_logical_edge(self, dic):
        """ Removes an logical edge from database and also removes the
            accompanying physical embedding

            Args:
                from_node (String): Name (label) of first node
                to_node (String): Name (label) of second node

            Raises:
                RuntimeError: Occurrence of error during transaction
        """
        node2 = self.store.find(
                NetworkNode,
                NetworkNode.id == dic['to_node']
                )
        node1 = self.store.find(
                NetworkNode,
                NetworkNode.id == dic['from_node']
                )

        node1 = node1[0]
        node2 = node2[0]

        edge = self.store.find(
                LogicalEdge,
                LogicalEdge.node_one_id == node1.id,
                LogicalEdge.node_two_id == node2.id
                )
        if edge.count() == 0:
            edge = self.store.find(
                    LogicalEdge,
                    LogicalEdge.node_one_id == node2.id,
                    LogicalEdge.node_two_id == node1.id
                    )

        if edge.count() == 0:
            raise RuntimeError('Error in data.dbinterfaces.StormConnector.' + \
                    'remove_logical_edge: No logical edge found start point ' + \
                    '{} and end point {}'.format(from_node, to_node)
                    )
        elif edge.count() > 1:
            for e in edge:
                self.remove_logical_edge_embedding(e.id)
                self.store.remove(e)
        else:
            self.remove_logical_edge_embedding(edge[0].id)
            self.store.remove(edge[0])

    def remove_logical_edge_embedding(self, logical_edge_id):
        """ Removes logical edge embedding.

            Args:
                logical_edge_id (int): Id of edge to remove
        """
        entries = self.store.find(
                LogicalEdgeEmbedding,
                LogicalEdgeEmbedding.logical_edge_id == logical_edge_id
                )
        for entry in entries:
            self.store.remove(entry)
        self.store.flush()

    def remove_physical_edge(self, edge_id):
        pass

    def remove_physical_port(self, port_id):
        pass

    def remove_physical_switch(self, switch_id):
        """ Removes switch and ports belonging to that switch

            Args:
                switch_id (int): Primary key of relation *PhysicalSwitch*

            Raises:
                AssertionError: ``switch_id`` not numeric
                RuntimeError: Error during transaction
        """
        try:
            switches_to_vsdns = self.store.find(
                    SwitchToVsdn,
                    SwitchToVsdn.switch_id == switch_id
                    ).remove()
        except Exception as e:
            raise RuntimeError('Error in data.dbinterfaces.StormConnector.' + \
                    '.remove_physical_switch : Error while attempting to remove ' + \
                    'Switch to VSDN mapping during removal of switch with ' + \
                    'id {}. Error message was {}'.format(switch_id, e.message)
                    )

        try:
            self.store.find(PhysicalPort, PhysicalPort.switch_id == switch_id).remove()
        except Exception as e:
            raise RuntimeError('Error in data.dbinterfaces.StormConnector.' + \
                    'remove_physical_switch: Error occured while removing ' + \
                    'Ports belonging to switch with ' + \
                    'id {}. Error message was {}'.format(switch_id, e.message)
                    )
        switch = self.store.get(NetworkNode, switch_id)
        self.store.remove(switch)
        switch = self.store.get(PhysicalSwitch, switch_id)
        if switch is not None:
            self.store.remove(switch)

    def remove_rate_limit(self, id):
        """ Removes RateLimit record from db

            Args:
                id (int): Primary key of record
        """
        self.store.remove(self.store.get(RateLimit, id))

    def remove_server(self, server_id):
        pass

    def remove_switch_to_vsdn(self, switch_id=None, vsdn_id=None):
        """ Removes mappings of switches to VSDNs from table ``SwitchToVsdn``

            If either ``switch_id`` or ``vsdn_id`` is not set, all matching
            records are removed

            Args:
                switch_id (int, optional): Switch for which mapping(s) should
                    be removed
                vsdn_id (int, optional): VSDN for which mapping(s) should be
                    removed.

            Raises:
                AssertionError if both ``switch_id`` and ``vsdn_id`` are None
        """
        assert (switch_id is not None) or (vsdn_id is not None), 'switch_id and ' + \
            'vsdn_id where None in StormConnector.remove_switch_to_vsdn'
        if switch_id is None:
            records = self.store.find(
                    SwitchToVsdn,
                    SwitchToVsdn.vsdn_id == vsdn_id
                    )
        elif vsdn_id is None:
            records = self.store.find(
                    SwitchToVsdn,
                    SwitchToVsdn.switch_id == switch_id
                    )
        else:
            records = self.store.find(
                    SwitchToVsdn,
                    SwitchToVsdn.switch_id == switch_id,
                    SwitchToVsdn.vsdn_id == vsdn_id
                    )
        for record in records:
            self.store.remove(record)

    def remove_tenant(self, tenant_id):
        pass

    def remove_vsdn(self, tenant_id=1, vsdn_id=None, vsdn_name=None):
        """ Removes VSDN record from respective relation as well as all other
            belonging entries:

            * hosts assigned to VSDN
            * Logical-Edges
            * Controller
            * Assignments of Switches

            Args:
                tenant_id (int): ID of tenant issuing request
                vsdn_id (int): Primary Key of relation
                vsdn_name (string): Name of vsdn to delete
        """
        def remove(vsdn):
            spaces = self.get_flow_visor_flow_space(vsdn_id=vsdn_id)
            for edge in vsdn.logical_edges:
                self.remove_logical_edge(edge.to_dictionary())

            for host in vsdn.get_hosts(self._store):
                self.store.remove(host)

            for space in spaces:
                for permission in space.slice_permissions:
                    self.store.remove(permission)
                self.store.remove(space.flowmatch)
                self.store.remove(space)

            self.remove_switch_to_vsdn(vsdn_id=vsdn_id)
            e = self.get_physical_edge(node_one_id=vsdn.controller.id)
            self.store.remove(e)
            self.store.remove(vsdn.controller.info)
            self.store.remove(vsdn.controller)
            self.store.remove(vsdn)
            self.store.flush()

        if vsdn_id is not None:
            vsdn = self.store.get(Vsdn, vsdn_id)
            remove(vsdn)
        elif vsdn_name is not None:
            vsdns = self.store.find(
                    Vsdn,
                    Vsdn.name == vsdn_name, Vsdn.tenant_id == tenant_id
                    )
            for vsdn in vsdns:
                remove(vsdn)
                
    def update_vsdn(self, vsdn, updates):
        if 'color' in updates.keys():
           self.store.find(Vsdn, Vsdn.id == vsdn.id).set(
               color=unicode(updates.pop('color'))
           )
        if 'message_rate' in updates.keys():
            self.store.find(Vsdn, Vsdn.id == vsdn.id).set(
                message_rate=int(updates.pop('message_rate'))
            )
        if 'isolation_method' in updates.keys():
            self.store.find(Vsdn, Vsdn.id == vsdn.id).set(
                isolation=int(updates.pop('isolation_method'))
            )
        self._logger.debug('updated vsdn')
                      


class AAAConnector(object):
    """ Establishes connection to database for AAA functionalitye
    """

    def __init__(self):
        """ Initializes object
        """
        self._config = data_config
        self._connection = storm.create_database(
                'mysql://{uname}:{pwd}@{host}:{port}/{schema}'.format(
                    uname = self._config['user'],
                    pwd = self._config['password'],
                    host = self._config['ip'],
                    port = self._config['port'],
                    schema = self._config['schema_name']
                    )
                )
        self._store = storm.Store(self._connection)

    def get_object(self, cls, id):
        """ Returns object of type ``cls``.

            Args:
                cls (classname): Any ORM class
                id (int): Id of object
        """
        element = self._store.get(cls, id)
        return element

    def get_objects(self, cls, where=[]):
        """ Searches databse of a set of objects with given restrictions.
            Restrictions are and combined.

            Args:
                cls (class): Class which should be retrieved
                where (list): List of restrictions

            Returns:
                objects: ordered storm.ResultSet after ID
        """
        objects = self._store.find(
                cls,
                *where
                ).order_by(cls.id)
        return objects


    def authenticate(self, username, password):
        """ Tries to verify identity of user

            Args:
                username (string): Name of user in system
                password (string): Password of user in system

            Returns:
                user: data.dbinterfaces.User instance or None if authenticate
                    failed

            Raises:
                RuntimeError if more than one user matches credentials
        """
        users = self._store.find(
                User,
                [
                    User.password == password,
                    User.name == username
                ])
        ret = None
        if users.count() > 1:
            raise RuntimeError('Multiple records for username {} found'.format(username))
        elif users.count() == 1:
            ret = users.one()
        return ret

    def authorize(self, user_id, action):
        """ Determines if user is authorized to perform action

            Args:
                user_id (int): Primary Key of user trying to perform action
                action (String): Action user wants to perform

            Returns:
                authorized: boolean, true if action could be authorized
        """
        authorized = False
        user = self.get_object(User, user_id)
        if action == 'new_user':
            if user.role == 'admin':
                authorized = True
        elif action == 'hvcontext':
            if user.role == 'admin':
                authorized = True
        elif action == 'get_all_vsdn':
            if user.role == 'admin':
                authorized = True

        return authorized

