""" Contains embedding algorithm
"""
import networkx as nx
import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir
    ))
import data.dbinterfaces as dbi
import management.hypervisor as hypervisor
import management.networkmanager
import logging
import json
import math
import numpy as np
logging.basicConfig(level=logging.DEBUG)

def get_admission_values(vsdn, connector):
    """ Gets the admission values for a VSDN request. The bitrate corresponding
        to message rate, the CPU utilization corresponding to message rate
        and the total amount of CPU allocated through all requests.

        Args:
            vsdn (data.dbinterfaces.Vsdn): Vsdn that was requested.
            connector (data.dbinterfaces.StormConnector): Database Connection

        Returns:
            bitrate, allocated_cpu for slice, used_cpu for all slices
    """
    try:
        used_cpu = vsdn.hypervisor.info.used_cpu
        hwe = HardwareIsolationEmbedding(vsdn, connector)
        prev_used_cpu = hwe._calculate_hypervisor_cpu(negative_rate=True)
        if vsdn.hypervisor.info.cfg_msg_rate - vsdn.message_rate == 0:
            allocated_cpu = used_cpu / vsdn.hypervisor.info.num_cores
        else:
            allocated_cpu = (used_cpu - prev_used_cpu) / vsdn.hypervisor.info.num_cores
        used_cpu /= vsdn.hypervisor.info.num_cores

        switch, port = hwe._retrieve_entities()
        bitrate, burst = hwe.calculate_limit(switch, False)
    except Exception as e:
        logging.exception('Error during calculation of admission values')
        bitrate = allocated_cpu = used_cpu = -1
    return bitrate, allocated_cpu, used_cpu


class EdgeEmbedding(object):

    def __init__(self, connection, logger_name, vsdn_id):
        self._connection = connection
        self._vsdn_id = vsdn_id
        self._logger = logging.getLogger(logger_name)

    def _construct_flowspace(self, nodes):
        """ Constructs new FlowSpaces and addes them to the database. FlowSpaces
            are defined for each switch using the slice's subnet.

            Args:
                nodes (List): List of physical switch ids

            Returns:
                flowspaces, List of dbi.FlowVisorFlowSpace objects or None if
                no spaces were required
        """
        missing = self._connection.get_missing_dpids(self._vsdn_id, nodes)
        flowspaces = []
        if missing.count() == 0:
            self._logger.info('No flowspaces for LogicalEdgeEmbedding for ' + \
                    'nodes {} and vsdn {}'.format(str(nodes), self._vsdn_id))
            return None
        else:
            vsdn = self._connection.get_vsdn(self._vsdn_id)
            for switch in missing:
                self._logger.info('Add flowspace for LogicalEdgeEmbedding ' + \
                        'for switch {} with id {} and vsdn {} with id {}'.format(
                            switch.name, switch.id, vsdn.name, vsdn.id))
                match = {
                        'nw_dst': vsdn.subnet,
                        'nw_src': vsdn.subnet
                        }
                match_id = self._connection.add_flow_visor_flow_match(match)

                space = {
                        'name': u'{}_{}'.format(vsdn.name, switch.id),
                        'dpid': switch.info.dpid,
                        'flowmatch_id': match_id,
                        'priority': 100
                        }
                space_id = self._connection.add_flow_visor_flow_space(**space)

                permission = {
                        'fvfs_id': space_id,
                        'vsdn_id': self._vsdn_id,
                        'permission': 7
                        }
                permission_id = self._connection.add_slice_permission(**permission)
                flowspaces.append(self._connection.store.get(
                    dbi.FlowVisorFlowSpace,
                    space_id
                    ))
        return flowspaces

    def embedd(self):
        pass

    def _find_embedding(self):
        pass


class EdgeEmbeddingFactory(object):
    """ Class producing specific EdgeEmbeeding types
    """
    @classmethod
    def produce(self, cplane, connection, vsdn_id, start_node_id,
            target_node_id, logical_edge_id):
        if cplane:
            return CPlaneEdgeEmbedding(connection, vsdn_id, start_node_id,
                    target_node_id, logical_edge_id)
        else:
            return LogicalEdgeEmbedding(connection, vsdn_id, start_node_id,
                    target_node_id, logical_edge_id)


class LogicalEdgeEmbedding(EdgeEmbedding):
    def __init__(self, connection, vsdn_id, start_node_id, target_node_id, logical_edge_id):
        super(LogicalEdgeEmbedding, self).__init__(connection, 'LogicalEdgeEmbedding', vsdn_id)
        self._hypervisor_stub = hypervisor.HypervisorFactory.produce()
        self._start_node_id = start_node_id
        self._target_node_id = target_node_id
        self._G = nx.Graph()
        self._logical_edge_id = logical_edge_id

    def _find_embedding(self):
        switches = self._connection.get_objects(
            dbi.PhysicalSwitch,
            [dbi.PhysicalSwitch.cplane == False]
            )
        switch_ids = [switch.id for switch in switches]
        edges = self._connection.get_switching_edges(switch_ids)

        # Step two add nodes and edges to graph
        self._G.add_nodes_from(switch_ids)
        self._G.add_edges_from([(e.node_one_id, e.node_two_id) for e in edges])
        path = nx.shortest_path(self._G, self._start_node_id, self._target_node_id)

        edges = []
        for i in range(len(path) - 1):
            edges.append(self._connection.get_physical_edge(path[i], path[i + 1]))

        return path, edges

    def embedd(self):
        """ Embed logical link and also adds everything to the databse

            Args:
                logical_link_id (int): Id of logical link going to be embedded

            Returns:
                List of switch_ids
        """
        switches, edges = self._find_embedding()
        edge_ids = [edge.id for edge in edges]
        flowspaces = self._construct_flowspace(switches)

        self._connection.add_logical_link_embedding(
                self._logical_edge_id,
                edge_ids
                )
        if flowspaces is not None:
            for space in flowspaces:
                self._hypervisor_stub.add_flowspace(space.to_request())
            self._logger.info((
                'Successfully created flowspaces and wrote state to database for ' + \
                'embedding of logical edge from {} to {}').format(
                    self._start_node_id,
                    self._target_node_id
                    )
            )
        else:
            self._logger.info((
                'Successfully wrote logical edge from {} to {} to database. ' + \
                'No flowspaces were required as respective ones are already ' + \
                'installed on relevant switches.'
                ).format(self._start_node_id, self._target_node_id)
            )
        return flowspaces


class CPlaneEdgeEmbedding(EdgeEmbedding):
    """ Class for embedding a logical link in the control plane. This type of
        link connects tennant controller to control network.
    """
    def __init__(self, connection, vsdn_id, start_node_id, target_node_id, logical_edge_id):
        """ Initializes object.

            Args:
                connection (data.dbinterfaces.StormConnector): connection to
                    database
                vsdn_id (int): Id for Vsdn edge belongs to
                start_node_id (int): ID of one endpoint of the edge
                target_node_id (int): ID of second endpoint of edge
                logical_edge_id (int): ID of corresponding logical edge
        """
        super(CPlaneEdgeEmbedding, self).__init__(connection, 'CPlaneEdgeEmbedding', vsdn_id)
        self._logical_edge_id = logical_edge_id
        node1 = self._connection.get_object(dbi.NetworkNode, start_node_id)
        node2 = self._connection.get_object(dbi.NetworkNode, target_node_id)
        self._switch = None
        self._controller = None
        if node1.info_type == 2:
            self._switch = self._connection.get_object(dbi.PhysicalSwitch, node1.id)
        elif  node1.info_type == 3:
            self._controller = self._connection.get_object(dbi.Controller, node1.id)
        else:
            raise KeyError('Wrong info type for first node of logical edge ' + \
                    'in control plane. expected 2 or 3 but got {}'.format(node1.info_type))
        if node2.info_type == 2:
            if self._switch is not None:
                raise RuntimeError('Duplicate switch for cplane edge')
            self._switch = self._connection.get_object(dbi.PhysicalSwitch, node2.id)
        elif  node2.info_type == 3:
            if self._controller is not None:
                raise RuntimeError('Duplicate controller for cplane')
            self._controller = self._connection.get_object(dbi.Controller, node2.id)
        else:
            raise KeyError('Wrong info type for second node of logical edge ' + \
                    'in control plane. expected 2 or 3 but got {}'.format(node1.info_type))
        self._logger.debug(self._switch.to_dictionary())

    def _nearest_control_switch(self, switch, control_switches):
        """ Returns list of switches sorted after the euclidean distance with
            respect to location of controller.

            Args:
                switch (data.dbi.PhysicalSwitch): Dataplane switch
                control_switches (storm.OrderedResultSet): control plane switches

            Returns:
                distances: List sorted after distance of control plane switches
                    to location of controller.
        """
        distances = []
        for sw in control_switches:
            d = math.sqrt(math.pow(sw.x - switch.x, 2) + math.pow(sw.y - switch.y, 2))
            distances.append((sw, d))
        distances.sort(key=lambda x: x[1])
        return distances

    def _get_next_free_port(self, switch):
        """ Returns free port for physical edge

            Args:
                switch (data.dbinterfaces.PhysicalSwitch): Control plane switch
                    serving as endpoint

            Returns:
                port: data.dbi.PhysicalPort
        """
        def query(id, p):
            where = []
            if p == 1:
                where.append(dbi.PhysicalEdge.port_one_id == id)
            else:
                where.append(dbi.PhysicalEdge.port_two_id == id)
            return self._connection.get_objects(
                    cls=dbi.PhysicalPort,
                    where=where
                    )

        for port in switch.info.ports:
            if query(port.id, 1).count() == 0:
                if query(port.id, 2).count() == 0:
                    return port
        #raise RuntimeError('No available port for control link to controller')
        return None

    def embedd(self):
        """ Embeds the logical link using the next free port on the
            geographically nearest control plane switch to the dataplane switch
        """
        tmp = self._connection.get_objects(
                cls=dbi.PhysicalSwitch
                )
        cswitches = [s for s in tmp if s.info.cplane]
        distances = self._nearest_control_switch(self._switch, cswitches)

        cport = None
        while (cport is None) and (len(distances) > 0):
            cswitch, distance = distances.pop(0)
            self._logger.info('Try switch {} with distsance {}'.format(
                cswitch.name,
                distance
                ))
            cport = self._get_next_free_port(cswitch)
        if cport is None:
            raise RuntimeError('No available port on any switch for control link to controller')

        edge = dbi.PhysicalEdge(
                node_one_id=self._controller.id,
                node_two_id=cswitch.id,
                port_two_id=cport.id
                )
        self._connection.store.add(edge)
        self._connection.store.flush()
        self._connection.add_logical_link_embedding(
                self._logical_edge_id,
                [edge.id]
                )
        self._logger.info((
                'CPlane Edge from {} to {} successfully ' + \
                'embedded.').format(self._switch.name, self._controller.name)
                )


class MessageRateEmbeddingFactory(object):
    """ Produces objects inheriting from MessageRateEmbedding class
    """

    @classmethod
    def produce(cls, vsdn, connector, isolation_method=None):
        """ Produces objects inheriting from MessageRateEmbedding class.

            Args:
                vsdn (data.dbinterfaces.Vsdn): Vsdn for which isolation should
                    be implemented.
                connector (data.dbinterfaces.StormConnector): Connector to database
                isolation_method (int, optional): Type of isolation that should
                    be implemented.

            Note:
                If argument ``isolation_method`` is set, the returned type will
                be ascertained based on ``isolation_method``. If it is not set
                the type of the limit will be inferred from the respective
                field in vsdn object.

            Returns:
                embedding: Subclass of MessageRateEmbedding class

            Raises:
                KeyError: If either ``vsdn.isolation_method`` or argument
                    ``isolation_method`` is not defined.
        """
        if isolation_method is None:
            isolation_method = vsdn.isolation_method

        if isolation_method == 1:
            return SoftwareIsolationEmbedding(vsdn, connector)
        elif isolation_method == 2:
            return HardwareIsolationEmbedding(vsdn, connector)
        else:
            raise KeyError(('Isolation method {} is undefined in ' + \
                    'MessageRateEmbeddingFactory').format(isolation_method))


class MessageRateEmbedding(object):
    """ Abstract superclass for embedding of message rates i.e. isolation of
        the bandwidth.

        Args:
            ratelimit (data.dbinterfaces.RateLimit): Object representing
                ratelimit which should be embedded
            logger (logging.Logger): Logger object
            vsdn (data.dbinterfaces.Vsdn): Object representing VSDN for
                which ratelimit should be embedded
            connector (data.dbinterfaces.StormConnector): Connector object
                to database
    """
    def __init__(self, vsdn, connector, logname):
        """ Initializes object.

            Args:
                logname (string): Name for the Logger
                vsdn (data.dbinterfaces.Vsdn): Object representing VSDN for
                    which ratelimit should be embedded
                connector (data.dbinterfaces.StormConnector): Connector object
                    to database
        """
        self._logger = logging.getLogger(logname)
        self._connector = connector
        self._vsdn = vsdn

    def remove(self):
        """ Removes the embedding
        """
        raise NotImplementedError('Function MessageRateEmbedding.remove not' +
                'implemented')

    def embed(self):
        """ Embeds the MessageRate according to isolation method
        """
        raise NotImplementedError('Function MessageRateEmbedding.embed not' +
                'implemented')

    def calculate_limit(self, entity):
        """ Calculates the limit message rate translates in unit of measurement
            corresponding to entity.

            entity (data.dbinterfaces.IterMixin): Physical entity message rate
                should be implemented on.
        """
        raise NotImplementedError('Function MessageRateEmbedding.embed not' +
                'implemented')

    def _calculate_hypervisor_cpu(self, negative_rate=False):
        """ Calculate the load requested message rate puts onto the hypervisor
            when getting accepted.

            Args:
                negative_rate (boolean): If set to True subtract requested
                    rate from implemented rate when calculating limit.

            Returns:
                cpu_stress: CPU utilization required for message rate
        """
        model = self._connector.get_regression_model(self._vsdn.hypervisor.info.model)
        coef = -1 if negative_rate else 1
        X = np.array([[coef * self._vsdn.message_rate + self._vsdn.hypervisor.info.cfg_msg_rate]])
        cpu_stress = model.predict(X)[0][0]
        return cpu_stress


class HardwareIsolationEmbedding(MessageRateEmbedding):
    """ Concrete implementation of ``MessageRateEmbedding`` for hardware isolation
        on a switch in the virtual SDN, i.e. the policer for the messsage rate
        of the controller in hardware

        Attributes:
            ratelimit (data.dbinterfaces.RateLimit): Object representing
                ratelimit which should be embedded
            logger (logging.Logger): Logger object
            vsdn (data.dbinterfaces.Vsdn): Object representing VSDN for
                which ratelimit should be embedded
            connector (data.dbinterfaces.StormConnector): Connector object
                to database
    """
    def __init__(self, vsdn, connector):
        """ Initializes object

            Args:
                vsdn (data.dbinterfaces.Vsdn): Object representing VSDN for
                    which ratelimit should be embedded
                connector (data.dbinterfaces.StormConnector): Connector object
                    to database
        """
        super(HardwareIsolationEmbedding, self).__init__(
                vsdn=vsdn,
                connector=connector,
                logname='HardwareIsolationEmbedding'
                )
        self._manager = management.networkmanager.NetworkmanagerFactory.produce()

    def _retrieve_entities(self):
        """ Retrieves necessary entities from database.

            Returns:
                switch: data.dbinterfaces.PhysicalSwitch tenant controller is
                    connecting to
                port: data.dbinterfaces.PhysicalPort tenant controller is
                    connected to
        """
        ledge = self._connector.get_logical_edges(self._vsdn.controller.id).one()
        edge = ledge.physical_embedding.one()
        switch = None
        if edge.node_one_id == self._vsdn.controller.id:
            switch_id = edge.node_two_id
            port = edge.port_two
        else:
            switch_id = edge.node_one_id
            port = edge.port_one

        switch = self._connector.get_object(dbi.PhysicalSwitch, switch_id)

        return switch, port

    def calculate_limit(self, entity, update=True):
        """ Calculates rate limit and burst based on the model of the switch

            entity (data,dbinterfaces.PhysicalSwitch): Switch for which limits
                should be calculated
            update (boolean): Set this if values should be updated (used if
                only limit and burst should be calculated).

            Returns:
                limit: Rate Limit in KB/s corresponding to message rate
                burst: Number of KB/s slice may exceed limit
        """
        model = self._connector.get_regression_model(entity.info.model)
        X = np.array([[self._vsdn.message_rate]])
        limit = model.predict(X)[0][0]
        burst = int(limit * 0.1)
        cpu_stress = self._calculate_hypervisor_cpu()

        if self._vsdn.hypervisor.info.total_cpu * 0.9 >= cpu_stress:
            # assign stress. Stress is calculated from sum of already
            # implemented and requested rate to capture jumps in CPU
            # utilization
            if update:
                self._vsdn.hypervisor.info.used_cpu = cpu_stress
                self._vsdn.hypervisor.info.cfg_msg_rate += self._vsdn.message_rate
        else:
            raise RuntimeError(('Requested message rate for hardware isolation ' + \
                    'too high, total: {}, used: {}, requested: {}, ' + \
                    'threshold: {}').format(
                        self._vsdn.hypervisor.info.total_cpu,
                        self._vsdn.hypervisor.info.used_cpu,
                        cpu_stress,
                        self._vsdn.hypervisor.info.total_cpu * 0.9
                        )
                    )

        return int(limit), int(burst)

    def remove(self):
        """ Removes the embedding
        """
        switch, port = self._retrieve_entities()

        self._manager.set_burst(switch.ip, switch.id, port.number, None)
        self._manager.set_rate_limit(switch.ip, switch.id, port.number, None)

        cpu_stress = self._calculate_hypervisor_cpu(negative_rate=True)
        self._vsdn.hypervisor.info.used_cpu = cpu_stress
        self._vsdn.hypervisor.info.cfg_msg_rate -= self._vsdn.message_rate

        self._logger.info( (
                'Successfully removed Hardware Isolation ' + \
                'on switch {} on port {}.'
                ).format(
                    switch.name,
                    port.number
                    )
                )

    def embed(self):
        """ Embeds the MessageRate according to isolation method
        """
        switch, port = self._retrieve_entities()
        limit, burst = self.calculate_limit(switch)
        self._manager.set_burst(
                switch.ip,
                switch.id,
                port.number,
                burst
                )
        self._manager.set_rate_limit(
                switch.ip,
                switch.id,
                port.number,
                limit
                )
        self._logger.info( (
                'Successfully embedded Hardware Isolation with limit {} ' + \
                'and burst {} on switch {} on port {}.'
                ).format(
                    limit,
                    burst,
                    switch.name,
                    port.number
                    )
                )


class SoftwareIsolationEmbedding(MessageRateEmbedding):
    """ Concrete implementation of ``MessageRateEmbedding`` for software isolation
        on a hypervisor node.

        Args:
            logger (logging.Logger): Logger object
            vsdn (data.dbinterfaces.Vsdn): Object representing VSDN for
                which ratelimit should be embedded
            connector (data.dbinterfaces.StormConnector): Connector object
                to database
    """
    def __init__(self, vsdn, connector):
        """ Initializes object

            Args:
                vsdn (data.dbinterfaces.Vsdn): Object representing VSDN for
                    which ratelimit should be embedded
                connector (data.dbinterfaces.StormConnector): Connector object
                    to database
        """
        super(SoftwareIsolationEmbedding, self).__init__(
                vsdn=vsdn,
                connector=connector,
                logname='SoftwareIsolationEmbedding'
                )

    def calculate_limit(self, entity, update=True):
        """ Calculates rate limit and burst based on the model of the switch

            entity (data,dbinterfaces.Hypervisor): Hypervisor providing ressources
                for slice.

            Returns:
                limit: Rate Limit in % of CPU
        """
        cpu_stress = self._calculate_hypervisor_cpu()

        if entity.info.total_cpu * 0.9 >= cpu_stress:
            # assign stress. Stress is calculated from sum of already
            # implemented and requested rate to capture jumps in CPU
            # utilization
            if update:
                entity.info.used_cpu = cpu_stress
                entity.info.cfg_msg_rate += self._vsdn.message_rate
            return self._vsdn.message_rate
        else:
            raise RuntimeError(('Requested message rate for software isolation ' + \
                    'too high, total: {}, used: {}, requested: {}, ' + \
                    'threshold: {}').format(
                        entity.info.total_cpu, entity.info.used_cpu, cpu_stress,
                        entity.info.total_cpu * 0.9)
                    )

    def remove(self):
        """ Removes the embedding
        """
        stub = management.hypervisor.HypervisorFactory\
                .produce(element=self._vsdn.hypervisor)
        stub.update_slice({'slice_name': self._vsdn.name, 'rate_limit': None})

        cpu_stress = self._calculate_hypervisor_cpu(negative_rate=True)
        self._vsdn.hypervisor.info.used_cpu = cpu_stress
        self._vsdn.hypervisor.info.cfg_msg_rate -= self._vsdn.message_rate

        self._logger.info('successfully removed Software Limint on ' + \
                'slice {}'.format(self._vsdn.name))

    def embed(self):
        """ Embeds the MessageRate according to isolation method
        """
        stub = management.hypervisor.HypervisorFactory\
                .produce(element=self._vsdn.hypervisor)
        limit = self.calculate_limit(entity=self._vsdn.hypervisor)
        self._logger.debug('Update slice {}, set rate limit to {}'.format(
            self._vsdn.name, limit))
        stub.update_slice({'slice_name': self._vsdn.name, 'rate_limit': limit})
        self._logger.info(('successfully embedded Software Isolation ' + \
                    'slice {}, rate {}.').format(self._vsdn.name, limit))

