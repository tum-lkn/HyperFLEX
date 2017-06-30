""" Defines global variables/constants and performs initialization
    (rading config files and such)
"""

def get_config():
    config = {}
    config['request_receiver_ip'] = 'localhost'
    config['request_receiver_port'] = 9469

    return config

