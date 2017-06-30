import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir,
    os.path.pardir
    ))
import data.dbinterfaces as dbinterfaces
import logging
from nose.tools import with_setup

logging.basicConfig(level=logging.DEBUG)

class TestFlowVisorFlowMatch(object):
    def test_to_cmd(self):
        space = dbinterfaces.FlowVisorFlowMatch()
        space.in_port = 100
        space.dl_src = u'192.168.0.77'

        print space.to_cmd()


class LogicalEdgeTest(object):
    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('LogicalEdgeTest')
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.info('setup LogicalEdgeTest classlevel')
        cls.connection = dbinterfaces.StormConnector()

    def test_nodes(self):
        ledge = self.connection.store.get(dbinterfaces.LogicalEdge, 34)
        nodes = ledge.physical_nodes
        for node in nodes:
            logging.debug('{}'.format(node))


class StormConnectorTest(object):
    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('StormConnectorTest')
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.info('set up classlevel')
        cls.connector = dbinterfaces.StormConnector()
        cls.logger.info('Done setting up classlevel')

    def teardown(cls):
        cls.logger.info('Start tearing down classlevel')
        cls.connector.store.rollback()
        cls.logger.info('Done tearing down classlevel')

    def test_get_physical_switches(self):
        nodes = self.connector.get_network_nodes([dbinterfaces.PhysicalSwitch])
        assert nodes.count() > 0, 'Not switches returned - check database'
        for node in nodes:
            self.logger.debug(node.name)

    def test_get_switching_edges(self):
        nodes = [1,2,3,4,5,6,8]
        edges = self.connector.get_switching_edges(nodes)
        for edge in edges:
            assert edge.node_one_id in nodes, 'ID {} is not in defined ' + \
                    'endpoints'.format(edge.node_one_id)
            assert edge.node_two_id in nodes, 'ID {} is not in defined ' + \
                    'endpoints'.format(edge.node_two_id)

    def test_get_missing_dpids(self):
        switch_ids = [1,2,3,4,5,6]
        missind_dpids = [
                '00:00:00:00:00:00:00:01',
                '00:00:00:00:00:00:00:02',
                '00:00:00:00:00:00:00:05',
                '00:00:00:00:00:00:00:06',
#                '00:00:00:00:00:00:00:08'
                ]
        switches = self.connector.get_missing_dpids(12, switch_ids)
        ids = [switch.id for switch in switches]
        assert switches.count() == len(missind_dpids), 'Number of returned ' + \
                'swtiches does not match. Expected {} got {} - {}'.format(
                        len(missind_dpids), switches.count(), str(ids))

        for switch in switches:
            logging.debug('id: {}, name: {}, dpid: {}'.format(
                switch.id, switch.name, switch.info.dpid))
            assert switch.info.dpid in missind_dpids, 'Returned switch\'s ' + \
                    'dpid not expected. DPID was: {}'.__format__(switch.info.dpid)

    def test_add_flow_visor_flow_match(self):
        vsdn = self.connector.store.get(dbinterfaces.Vsdn, 12)
        args = {
                'nw_dst': vsdn.subnet,
                'nw_src': vsdn.subnet
                }
        id = self.connector.add_flow_visor_flow_match(args)
        match = self.connector.store.get(dbinterfaces.FlowVisorFlowMatch, id)
        assert match is not None, 'No flow match found'
        assert match.nw_dst == vsdn.subnet, 'Destination does not match'
        assert match.nw_src == vsdn.subnet, 'Source does not match'

    def test_add_flow_visor_flow_space(self):
        self.logger.info('set up for add flow space')
        vsdn = self.connector.store.get(dbinterfaces.Vsdn, 12)
        args = {
                'nw_dst': vsdn.subnet,
                'nw_src': vsdn.subnet
                }
        flow_match_id = self.connector.add_flow_visor_flow_match(args)

        space = {
                'name': u'{}_{}'.format(vsdn.name, 1111),
                'dpid': u'11:11:11:11:11:11:11:11',
                'flowmatch_id': flow_match_id,
                'priority': 100
                }
        id = self.connector.add_flow_visor_flow_space(**space)
        space = self.connector.store.get(dbinterfaces.FlowVisorFlowSpace, id)
        assert space.name is not None, 'Space could not be found'

    def test_add_slice_permission(self):
        self.logger.info('set up for add slice permission')
        vsdn = self.connector.store.get(dbinterfaces.Vsdn, 12)
        args = {
                'nw_dst': vsdn.subnet,
                'nw_src': vsdn.subnet
                }
        flow_match_id = self.connector.add_flow_visor_flow_match(args)

        space = {
                'name': u'{}_{}'.format(vsdn.name, 1111),
                'dpid': u'11:11:11:11:11:11:11:11',
                'flowmatch_id': flow_match_id,
                'priority': 100
                }
        space_id = self.connector.add_flow_visor_flow_space(**space)


        permission = {
                'fvfs_id': space_id,
                'vsdn_id': vsdn.id,
                'permission': 7
                }
        permission_id = self.connector.add_slice_permission(**permission)
        permission = self.connector.store.get(dbinterfaces.SlicePermission, permission_id)
        assert permission is not None, 'Returned permission is None'

    def test_add_flowspace_request(self):
        self.logger.info('set up for add slice permission')
        vsdn = self.connector.store.get(dbinterfaces.Vsdn, 12)
        args = {
                'nw_dst': vsdn.subnet,
                'nw_src': vsdn.subnet
                }
        flow_match_id = self.connector.add_flow_visor_flow_match(args)

        space = {
                'name': u'{}_{}'.format(vsdn.name, 1111),
                'dpid': u'11:11:11:11:11:11:11:11',
                'flowmatch_id': flow_match_id,
                'priority': 100
                }
        space_id = self.connector.add_flow_visor_flow_space(**space)

        permission = {
                'fvfs_id': space_id,
                'vsdn_id': vsdn.id,
                'permission': 7
                }
        permission_id = self.connector.add_slice_permission(**permission)
        space = self.connector.store.get(dbinterfaces.FlowVisorFlowSpace, space_id)
        command = space.to_request()
        self.logger.debug(str(command))


class RegressionModelTest(object):
    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('RegressionModelTest')
        cls.con = dbinterfaces.StormConnector()

    def test_model_retrieval():
        
