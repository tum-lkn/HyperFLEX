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
import hyperflexcore.intelligence.embedding as embedding
import hyperflexcore.data.dbinterfaces as dbi
import json
logging.basicConfig(level=logging.DEBUG)

class LogicalEdgeEmbeddingTest(object):
    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('LogicalEdgeEmbeddingTest')
        cls.logger.setLevel(logging.DEBUG)
        cls.logger.info('Start set up class level')
#        cls.connection = dbi.StormConnector()
        cls.embedding = embedding.LogicalEdgeEmbedding(
                vsdn_id=12,
                start_node_id=1,
                target_node_id=8,
                logical_edge_id=33
                )
        cls.logger.info('Done setting up class level')

    @classmethod
    def teardown(cls):
        cls.logger.info('Tearing class LogicalEdgeEmbedding down')
        cls.embedding._connection.store.rollback()

    def test_find_embedding(self):
        path = self.embedding._find_embedding()
        self.logger.debug(str(path))

    def test_construct_flowspace(self):
        nodes = [1,4,8]
        spaces = self.embedding._construct_flowspace(nodes)
        print len(spaces)
        assert len(spaces) == 2, 'Wrong number of flospaces, expected {}, ' + \
                'but got {}'.format(len(nodes), len(spaces))
        for space in spaces:
            self.logger.debug(json.dumps(space.to_request(), indent=1))


class HardwareIsolationTest(object):
    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('HardwareIsolationTest')
        cls.logger.setLevel(logging.DEBUG)
        connector = dbi.StormConnector()
        vsdn = connector.get_object(dbi.Vsdn, 12)
        cls.embedding = embedding.HardwareIsolationEmbedding(vsdn, connector)

    def test_retrieve_entities(self):
        switch, port = self.embedding._retrieve_entities()
        assert port.id == 219, 'Wrong port, given {} instead of {}'.format(port.id, 219)
        assert switch.id == 4, 'Wrong switch, wanted {}, got {}'.format(
                4, switch.id)
        assert type(switch) == dbi.NetworkNode, 'Wrong class: {}'.format(type(switch))

    def test_calculate_limit(self):
        limit, burst = self.embedding.calculate_limit(None)
        l = 624 * 1000
        b = int(l*0.1)
        assert limit == l, 'Wrong limit, wanted {} got {}'.format(l, limit)
        assert burst == b, 'Wrong burst, wanted {} got {}'.format(b, burst)

    def test_embed_limit(self):
        self.embedding.embed()

    def test_remove_limit(self):
        self.embedding.remove()


class SoftwareIsolationTest(object):
    @classmethod
    def setup(cls):
        cls.logger = logging.getLogger('HardwareIsolationTest')
        cls.logger.setLevel(logging.DEBUG)
        connector = dbi.StormConnector()
        vsdn = connector.get_object(dbi.Vsdn, 12)
        cls.embedding = embedding.SoftwareIsolationEmbedding(vsdn, connector)

    def test_calculate_limit(self):
        limit = self.embedding.calculate_limit(None)

    def test_embed_limit(self):
        self.embedding.embed()

    def test_remove_limit(self):
        self.embedding.remove()
