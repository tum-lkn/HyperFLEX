""" This module processes requests made by users through the gui. The main
    taks of this module is to orchestrate operations (adding logical link -->
    get embedding --> write embedding) for writing and retrieving of data
"""
import sys
import os
import random
sys.path.insert(
        0,
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)
        )
import management.hypervisor as hvapi
import management.networkmanager as nwmgmtapi
import intelligence
import embedding
import management.management as mgmt
import data.dbinterfaces as dbi
import json
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class ManagementGuiControllerHandler:
    """ Handles persisting and triggering of processes related to GUI events.
        Uses `intelligence` module to identify embedding but handles persisting
        of changes into the db itself.
    """

    def __init__(self):
        self._connector = dbi.StormConnector()
        self._hvstub = hvapi.HypervisorFactory.produce()
        self._nwmgmtstub = nwmgmtapi.NetworkmanagerFactory.produce()
        self._logger = logging.getLogger('MgmtGuiControllerHandler')

    def process_network_change_request(self, request):
        """ Handles changes to the network topology (adding links, switches,
            and other elements).

            Args:
                request (Dictionary): Dictionary of Lists of Dictionaries

            Raises:
                AssertionError:
                    key ``vsdn_id`` not present in request
                    ``vsdn_id`` not an integer
        """
        node_removals = []
        node_inserts = []
        edge_inserts = []
        edge_removals = []
        for key, value in request.iteritems():
            if key == 'nodes':
                for dic in value:
                    if dic['action'] == 'remove':
                        node_removals.append(dic)
                    elif dic['action'] == 'add':
                        node_inserts.append(dic)
            elif key == 'edges':
                for dic in value:
                    if dic['action'] == 'remove':
                        edge_removals.append(dic)
                    elif dic['action'] == 'add':
                        edge_inserts.append(dic)
            elif key == 'vsdn':
                pass
            else:
                raise ValueError((
                    'Unexpected keyword {}. Expected "nodes" or "edges"'
                    ).format(key)
                    )
        dc = self._connector
        err = False

        vsdn_id = request['vsdn']['id']

        if len(request['vsdn']) > 1:
            # If dictionary contains more than the vsdn id
            try:
                self._process_vsdn_update(request['vsdn'])
            except Exception as e:
                self._logger.exception('Error during update of VSDN ' + \
                        'settings. Error was {}'.format(e.message))
                dc.store.rollback()
                err = True
                raise RuntimeError('Error during VSDN update. Error was: {}'.format(e.message))

        if len(edge_removals) > 0:
            try:
                self._process_edge_removals(edge_removals, vsdn_id)
            except Exception as e:
                dc.store.rollback()
                self._logger.exception('Error during removal of edges ' + \
                        'settings. Error was {}'.format(e.message))
                err = True
                raise RuntimeError('Error during removal of edges. Error was: {}'.format(e.message))

        if len(node_removals) > 0:
            try:
                self._process_node_removals(node_removals, vsdn_id)
            except Exception as e:
                dc.store.rollback()
                self._logger.exception('Error during removal of nodes ' + \
                        'settings. Error was {}'.format(e.message))
                err = True
                raise RuntimeError('Error during removal of nodes. Error was: {}'.format(e.message))

        if len(node_inserts) > 0:
            try:
                self._process_node_inserts(node_inserts, vsdn_id)
            except Exception as e:
                dc.store.rollback()
                self._logger.exception('Error during inserting of new nodes ' + \
                        'settings. Error was {}'.format(e.message))
                err = True
                raise RuntimeError('Error during inserting of nodes. Error was: {}'.format(e.message))

        if len(edge_inserts) > 0:
            try:
                self._process_edge_inserts(edge_inserts, vsdn_id)
            except Exception as e:
                self._logger.exception('Error during embedding of new edges ' + \
                        'settings. Error was {}'.format(e.message))
                dc.store.rollback()
                err = True
                raise RuntimeError('Error during inserting of edges. Error was: {}'.format(e.message))

        if not err:
            self._logger.debug('Commit Updates')
            dc.store.commit()

    def _process_vsdn_update(self, updates):
        """ Processes updates on a VSDN.

            Args:
                updates (dict): Dictionary with updates
                vsdn_id (int): Id of Vsdn
        """
        vsdn = self._connector.get_vsdn(int(updates.pop('id')))
        vsdn_dic = updates
        old_isolation = None
        update_isolation = False

        if 'isolation_method' in vsdn_dic.keys():
            self._logger.debug('changed isolation from {} to {}'.format(
                old_isolation, vsdn_dic['isolation_method']
            ))
            self._logger.debug('Stoer away old isolation method')
            old_isolation = vsdn.isolation_method
            update_isolation = True
        if 'message_rate' in vsdn_dic.keys():
            update_isolation = True

        self._connector.update_vsdn(vsdn, vsdn_dic)

        if update_isolation:
            if old_isolation is not None:
                self._logger.debug('remove old isolation')
                embd = embedding.MessageRateEmbeddingFactory.produce(
                        vsdn,
                        self._connector,
                        old_isolation
                        )
                embd.remove()
            embd = embedding.MessageRateEmbeddingFactory.produce(vsdn, self._connector)
            embd.embed()

    def _push_isolation(self, vsdn, old_method=None):
        """ Pushes a new isolation and resets old one.

            Args:
                vsdn (data.dbinterfaces.RateLimit): Vsdn for which limit shoul
                    be changed
                old_method (int): Old method which should be reset
        """
        method = vsdn.isolation_method
        limit = vsdn.rate_limit
        if old_method is not None and old_method != method:
            if old_method == 1:
                args = {'slice_name': vsdn.name, 'rate_limit': None}
                self._hvstub.update_slice(args)
            elif old_method == 2:
                self._nwmgmtstub.set_rate_limit(1, 3, None)
                self._nwmgmtstub.set_burst(1, 3, None)

        if method == 1:
            args = {'slice_name': vsdn.name, 'rate_limit': limit.rate_limit}
            self._hvstub.update_slice(args)
        elif method == 2:
            self._nwmgmtstub.set_rate_limit(1, 3, limit.rate_limit)
            self._nwmgmtstub.set_burst(1, 3, limit.burst)

    def _process_node_removals(self, removals, vsdn_id):
        """ Prepares removals for Database Interface

            Args:
                request (List): List of Dictionaries
                vsdn_id (int): Primary Key to *Vsdn* relation

            Raises:
                ValueError: unknown value of field ``type`` encountered
        """
        dc = self._connector
        for dic in removals:
            if dic['type'] == 'switch':
                dc.remove_switch_to_vsdn(dic['id'], vsdn_id)
            elif dic['type'] == 'controller':
                dc.remove_controller(dic['id'], vsdn_id)
            elif dic['type'] == 'hypervisor':
                dc.remove_hypervisor(dic['id'])
            elif dic['type'] == 'server':
                dc.remove_server(dic['id'])
            elif dic['type'] == 'host':
                dc.remove_host(dic['id'])
            else:
                raise ValueError(
                        'Error in itelligence.guihandling.ManagementGuiControllerHandler' +
                        'Unknown type encountered while removing ' +
                        'nodes. Keyword was: {}'.format(dic['type'])
                        )

    def _process_node_inserts(self, inserts, vsdn_id, ctrl_access=None,
            ctrl_ip=None, ctrl_port=None):
        """ Processes insert requests

            Args:
                inserts (List): List of dictionaries
                vsdn_id (int): Primary Key of *Vsdn* relation
                ctrl_access (int, optional): In case controller is added,
                    supply access point
                ctrl_ip (int, optional): In case controller is added supply ip
                ctrl_port (int, optional): In case controller is added
                    supply port

            Returns:
                resolve, dictionary resolving old ids from GUI to actual IDs from DB
            Raises:
                ValueError: Unknown value for field ``type`` encountered
        """
        dc = self._connector
        resolve = {}
        for dic in inserts:
            if dic['type'] == 'switch':
                dc.add_switch_to_vsdn(dic['id'], vsdn_id)
            elif dic['type'] == 'controller':
                dic['ip'] = ctrl_ip
                dic['ip_port'] = ctrl_port
                dic['entry_point'] = ctrl_access
                new_id = dc.add_controller(dic, vsdn_id)
                resolve[dic['id']] = new_id
            else:
                raise ValueError('Unknown keyword {} encountered while adding ' + \
                        'network noes'.format(dic['type'])
                        )
        return resolve

    def _process_edge_inserts(self, inserts, vsdn_id):
        """ Processes insertion of new logical edges

            Args
                inserts (List): List of dictionaries
                vsdn_id (int): Primary key for relation *Vsdn*
        """
        for insert in inserts:
            print insert
            # make sure from/to are ints
            insert['from_node'] = int(insert['from_node'])
            insert['to_node'] = int(insert['to_node'])
            edge_id = self._connector.add_logical_edge(insert, vsdn_id)
            n1 = self._connector.get_object(dbi.NetworkNode, insert['from_node'])
            n2 = self._connector.get_object(dbi.NetworkNode, insert['to_node'])

            if n1.info_type == n2.info_type:
                insert['cplane'] = False

            else:
                insert['cplane'] = True

            cplane = insert['cplane'] if 'cplane' in insert else False
            ebd = embedding.EdgeEmbeddingFactory.produce(
                    cplane,
                    self._connector,
                    vsdn_id=vsdn_id,
                    start_node_id=insert['from_node'],
                    target_node_id=insert['to_node'],
                    logical_edge_id=edge_id
                    )
            ebd.embedd()

    def _process_edge_removals(self, removals, vsdn_id):
        """ Removes physical edge from database

            Args:
                removals (List): List of dictionaries
                vsdn_id (int): Primary Key to relation *Vsdn*
        """
        for removal in removals:
            self._connector.remove_logical_edge(removal)

    def _flush_ids(self, edges, resolve):
        """ After insertion of new nodes replace old IDs with new IDs

            Args:
                edges (List): List of dictionaries
                resolve (dictionary): Dictionary mapping GUI IDs to DB IDs
        """
        for edge in edges:
            if edge['to_node'] in resolve.keys():
                edge['to_node'] = resolve[edge['to_node']]
            if edge['from_node'] in resolve.keys():
                edge['from_node'] = resolve[edge['from_node']]

    def _vsdn_to_dict(self, vsdn):
        """ Returns dictionary with entries ``vsdn``, ``nodes`` and ``edges``

            Args:
                vsdn (dbinterfaces.Vsdn): Vsdn class

            Returns:
                dictionary containing:
                    vsdn, vsdn itself as dictionary
                    nodes, list of nodes
                    edges, list of edges
        """
        nodes = []
        edges = []

        for switch in vsdn.switches:
            nodes.append(switch.to_dictionary())
        hosts = vsdn.get_hosts(self._connector.store)

        for host in hosts:
            nodes.append(host.to_dictionary())
        nodes.append(vsdn.controller.to_dictionary())

        for edge in vsdn.logical_edges:
            edges.append(edge.to_dictionary())

        return {
            'vsdn':vsdn.to_dictionary(),
            'nodes':nodes,
            'edges':edges
            }

    def get_all_tenant_vsdn_topos(self, tenant_id):
        """ Returns all topologies (hosts, logiacl links) of all VSDNs belonging
            to a specific tenant

            Args:
                tenant_id (int): Primary key for relation *Tenant*

            Returns:
                Dictionary of Lists
        """
        dc = self._connector
        vsdns = dc.get_vsdns_of_tenant(tenant_id)
        ret_vsdns = []
        for vsdn in vsdns:
            ret_vsdns.append(self._vsdn_to_dict(vsdn))
        return ret_vsdns

    def get_all_vsdn_topos(self):
        """ Returns all stored VSDN topologies

            Returns:
                List of Dictionaries
        """
        vsdns = self._connector.get_all_vsdns()
        ret_vsdns = []
        for vsdn in vsdns:
            ret_vsdns.append(self._vsdn_to_dict(vsdn))
        return ret_vsdns

    def get_vsdn_topo(self, vsdn_id):
        """ Returns one specific VSDN topology (Hosts, LogicalEdges)

            Args:
                vsdn_id (int): Primary Key to relation *Vsdn*

            Returns:
                Dictionary of Lists
        """
        dc = self._connector
        nodes = []
        edges = []

        vsdn = dc.get_vsdn(vsdn_id)
        for switch in vsdn.switches:
            nodes.append(switch.to_dictionary())

        for host in vsdn.get_hosts(dc.store):
            nodes.append(host.to_dictionary())
        nodes.append(vsdn.controller.to_dictionary())

        for edge in vsdn.logical_edges:
            edges.append(edge.to_dictionary())

        return {'vsdn':vsdn.to_dictionary(), 'nodes':nodes, 'edges':edges}

    def get_control_plane(self):
        """ Returns physical topology of control plane

            Returns:
                control: dictionary representing control plane
        """
        switches, edges = self._connector.get_physical_topo(cplane=True)
        for e in edges:
            print e.id
        nodes = [s.to_dictionary() for s in switches]
        redges = [e.to_dictionary() for e in edges]
        return {'nodes': nodes, 'edges':redges}

    def get_data_plane(self, vsdn_id=None):
        """ Returns the physical topology (switches and physical edges) allocated
            to a specific VSDN

            Args:
                vsdn_id (int, optional): Primary Key to relation *Vsdn*

            Note:
                At the moment whole physical topology is returned. At a later
                point this behaviour will change

            Returns:
                Dictionary of Lists
        """
        dc = self._connector
        nodes = []
        ret_edges = []
        switches, edges = dc.get_physical_topo()

        for switch in switches:
            nodes.append(switch.to_dictionary())

        for edge in edges:
            ret_edges.append(edge.to_dictionary())

        return {'nodes':nodes, 'edges':ret_edges}

    def get_hypervisor_context(self, vsdn_id=None):
        """ Returns all hypervisor and edges starting at it from database (for
            a specific VSDN

            Args:
                vsdn_id (int, optional): Primary key of the *Vsdn* relation

            Returns:
                hdics: List of dictionaries containing attributes of Hypervisor
                edges: List of edges
        """
        dc = dbi.StormConnector()
        hypervisor = dc.get_hypervisor()
        hdics = []
        edges = []
        for h in hypervisor:
            hdics.append(h.to_dictionary())
            set = dc.get_edges_by_node(h.id)
            for e in set:
                edges.append(e.to_dictionary())
        return hdics, edges

    def new_vsdn(self, args):
        vsdn_id = None
        vsdn_dic = args['vsdn']
        nodes = args['nodes']
        edges = args['edges']
        err = False
        hv = hvapi.HypervisorFactory.produce()
        do_hv_rollback = False
        embd = None

        if 'tenant_id' not in vsdn_dic.keys():
            vsdn_dic['tenant_id'] = 1
        if 'color' not in vsdn_dic.keys():
            r = lambda: random.randint(100,255)
            vsdn_dic['color'] = u'%02X%02X%02X' % (r(),r(),r())
        if 'hypervisor_id' not in vsdn_dic.keys():
            vsdn_dic['hypervisor_id'] = 10

        ctrl = None
        for node in nodes:
            if node['type'] == 'controller':
                ctrl = node
                break
        if ctrl is None:
            raise AttributeError('No Controller specified for slice {}'.format(vsdn['name']))

        try:
            vsdn_id = self._connector.add_vsdn(vsdn_dic)
            vsdn = self._connector.get_vsdn(vsdn_id)

            resolve = self._process_node_inserts(
                    inserts=nodes,
                    vsdn_id=vsdn_id,
                    ctrl_access=int(vsdn_dic['ctrl_access']),
                    ctrl_ip=vsdn_dic['ctrl_ip'],
                    ctrl_port=int(vsdn_dic['ctrl_port'])
                    )
            self._logger.info('Nodes successfully added to database')
            self._flush_ids(edges, resolve)

            hv.add_slice(vsdn)
            do_hv_rollback = True
            self._logger.info('Slice succesfully pushed to hypervisor')

            self._process_edge_inserts(inserts=edges, vsdn_id=vsdn_id)
            self._logger.info('Logical Edges successfully added to database' + \
                    'and embedded on hypervisor')

            embd = embedding.MessageRateEmbeddingFactory.produce(
                    vsdn=vsdn,
                    connector=self._connector
                    )
            if isinstance(embd, embedding.SoftwareIsolationEmbedding):
                self._logger.info('Wait for three seconds to give flowvisor ' + \
                        'time to do whatever it does')
                time.sleep(3)
            embd.embed()
            self._logger.info('Isolation successfully embedded')

            bitrate, allocated_cpu, used_cpu = embedding.get_admission_values(
                    vsdn=vsdn,
                    connector=self._connector
                    )
            vsdn.bitrate = bitrate
            vsdn.allocated_cpu = allocated_cpu
        except Exception as e:
            self._logger.exception('Error during VNR, error was {}'.format(e.message))
            if embd is not None:
                embd.remove()
            if do_hv_rollback:
                hv.remove_slice(vsdn)
                self._logger.info('Hypervisor set back')
            self._connector.store.rollback()
            err = True
            vsdn_id = None
            raise RuntimeError('Error during adding of new vsdn. ' + \
                    'Error was: {0}'.format(e)
                    )
        if not err:
            self._connector.store.commit()
            self._logger.info('Commited Database Changes')
            #return {
            #        'id': vsdn_id,
            #        'bitrate': bitrate,
            #        'usedcpu': used_cpu,
            #        'allocatedcpu': allocated_cpu
            #        }
            return vsdn_id

    def remove_vsdn(self, tenant_id, vsdn_id):
        err = True
        try:
            vsdn = self._connector.get_object(dbi.Vsdn, vsdn_id)
            embd = embedding.MessageRateEmbeddingFactory.produce(vsdn, self._connector)
            embd.remove()
            self._logger.info('Isolation removed')

            hv = hvapi.HypervisorFactory.produce()
            hv.remove_slice(vsdn)
            self._logger.info('Hypervisor setting removed')
            vsdn = None
            self._connector.remove_vsdn(vsdn_id=vsdn_id)
        except Exception as e:
            self._logger.exception('Error during removal of VSDN')
            self._connector.store.rollback()
            msg = 'Error while removing VSDN. Error was: {0}'.format(e)
            err = False
            raise RuntimeError(msg)

        if err:
            self._connector.store.flush()
            self._connector.store.commit()
        return err

