""" Standalone Thread representing intelligence in HyperFLEX.
"""
import sys
import os
import math
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.path.pardir
    ))
import management.hypervisor as hvapi
import data.dbinterfaces as dbi
import threading
import logging

def calculate_rate_limit(vsdn, connection):
    """ Sets rate limit for a given isolation technique and message rate and
        writes it to database.
        Sets respective attributes in vsdn object.

        Args:
            vsdn (data.dbinterfaces.Vsdn): Vsdn for which to calculate limit
            connection (data.dbinterfaces.StormConnector): Used to insert
                RateLimits and update slice
    """
    limit = -1
    burst = 0
    if vsdn.isolation == 1:
        limit, burst = calculate_software_rate_limit(vsdn)
    elif vsdn.isolation == 2:
        limit, burst = calculate_hardware_rate_limit(vsdn)
    else:
        raise KeyError((
                    'Unknown isolation method {} in intelligence.' + \
                    'calculate_rate_limit'
                    ).format(vsdn.isolation_method)
                )
    id = connection.add_rate_limit(limit, burst)
    if vsdn.rate_limit_id is not None:
        connection.remove_rate_limit(vsdn.rate_limit_id)
    vsdn.rate_limit_id = id

def calculate_software_rate_limit(vsdn):
    """ Calculates the rate limit for software isolation

        Args:
            vsdn (data.dbinterfaces.Vsdn): Vsdn for which to calculate limit

        Returns:
            limit: integer representing CPU utilization in %
            burst: Integer represeting how much CPU slice can use beyond limit
    """
    limit = int(vsdn.message_rate * 0.0375)
    burst = 0
    if limit > 50:
        raise RuntimeError('Requested message rate for software isolation' +
                'too high')
    return limit, burst

def calculate_hardware_rate_limit(vsdn):
    """ Calculates rate limit for hardware isolation

        Args:
            vsdn (data.dbinterfaces.Vsdn): Vsdn for which to calculate limit

        Returns:
            limit: integer representing Kb per second
            burst: Integer reprsenting how many Kb/second port can go beyond limit
    """
    limit = vsdn.message_rate * 624
    burst = int(limit * 0.1)
    if limit > 831792:
        raise RuntimeError('Requested message rate for hardware isolation' +
                'too high')

    return limit, burst

class AbstractThread(threading.Thread):

    def __init__(self, logger_name):
        super(AbstractThread, self).__init__()
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.INFO)


class VsdnImplementationThread(AbstractThread):
    """ Handles jobs during startup of HyperFLEX.

        At the moment this is pushing defined VSDNs to configured Hypervisor
        instances
    """
    def __init__(self):
        super(VsdnImplementationThread, self).__init__('vsdn_impl_logger')

    def run(self):
        connector = dbi.StormConnector()
        hvs = []
        hv = hvapi.HypervisorFactory.produce()

        vsdns = connector.get_all_vsdns()
        for vsdn in vsdns:
            if vsdn.name != 'test':
                continue
            slice_args = {
                    'slice_name': vsdn.name,
                    'controller_url': 'tcp:{}:{}'.format(
                        vsdn.controller.ip,
                        vsdn.controller.info.ip_port
                        ),
                    'admin_contact': 'contact@admin.com',
                    'password': 'password'
                    }
            hv.add_slice(slice_args)

        self._logger.debug('Done with slices, go to spaces')
        spaces = connector.get_flow_visor_flow_space()
        for space in spaces:
            flow_args = space.to_request()
            hv.add_flowspace(flow_args)


class IntelligenceThread(AbstractThread):
    """ Main loop
    """
    def __init__(self):
        super(IntelligenceThread, self).__init__('IntelligenceThread')

    def run(self):
        self._logger.info('Begin Bootstrapping')
        vsdn_impl = VsdnImplementationThread()
        vsdn_impl.start()

        vsdn_impl.join()
        self._logger.info('Done Bootstrapping, start loop')

        self._logger.info('Goodbye')


if __name__ == '__main__':
    t = IntelligenceThread()
    t.run()
