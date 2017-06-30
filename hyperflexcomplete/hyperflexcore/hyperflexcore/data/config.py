""" Defines configurational stuff for other modules in this package
"""

def get_config_hyperflex_topo_simple():
    hyperflex_topo_simple = {}
    hyperflex_topo_simple['ip'] = 'localhost'
    hyperflex_topo_simple['port'] = '3306'
    hyperflex_topo_simple['user'] = 'root'
    hyperflex_topo_simple['password'] = 'root'

    hyperflex_topo_simple['schema_name'] = 'HyperFlexTopologySimple'
    hyperflex_topo_simple['tbl_host'] = 'NetworkNode'
    hyperflex_topo_simple['tbl_link'] = 'Link'
    hyperflex_topo_simple['tbl_network_node'] = 'NetworkNode'
    hyperflex_topo_simple['tbl_switch'] = 'NetworkNode'
    hyperflex_topo_simple['tbl_vsdn'] = 'Vsdn'

    return hyperflex_topo_simple

def get_config_hyperflex_topo():
    hyperflex_topo = {}
    hyperflex_topo['ip'] = '10.162.149.80'
    hyperflex_topo['port'] = '3306'
    hyperflex_topo['user'] = 'root'
    hyperflex_topo['password'] = 'openflow'

    hyperflex_topo['schema_name'] = 'HyperFlexTopologyDevelop'
    hyperflex_topo['switch_info_type'] = 2
    hyperflex_topo['host_info_type'] = 1
    hyperflex_topo['controller_info_type'] = 3
    return hyperflex_topo

def get_default_controller_port():
    return 9000

def default_switch_ip_prefix():
    return '192.168.0.'

def default_switch_ip_port():
    return 9100
