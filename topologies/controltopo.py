#!/usr/bin/python

"""
This example shows how to add an interface (for example a real
hardware interface) to a network after the network is created.
"""

import re
import sys

from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.link import Intf
from mininet.util import quietRun
from mininet.node import OVSController
from mininet.topo import Topo
#sys.path.append("/home/mininet/pox/")
#from pox import POX

class ControlTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."
        # Initialize topology
        Topo.__init__( self )
        #self.addController()
        # Add hosts and switches
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')
        switch4 = self.addSwitch('s4')
        switch5 = self.addSwitch('s5')
#        switch6 = self.addSwitch('s6')

#        h1 = self.addHost('h1')
#        h2 = self.addHost('h2')
        # Add links
        #self.addLink( rightSwitch, leftSwitch )
        self.addLink(switch1, switch3)
        self.addLink(switch2, switch3)
#        self.addLink(switch3, switch3)
        self.addLink(switch4, switch3)
        self.addLink(switch5, switch3)
#        self.addLink(switch5, h1)
#        self.addLink(switch4, h2)
        
topos = { 'ctrl-topo': ( lambda: ControlTopo() ) }

def checkIntf( intf ):
    "Make sure intf exists and is not configured."
    if ( ' %s:' % intf ) not in quietRun( 'ip link show' ):
        error( 'Error:', intf, 'does not exist!\n' )
        exit( 1 )
    ips = re.findall( r'\d+\.\d+\.\d+\.\d+', quietRun( 'ifconfig ' + intf ) )
    if ips:
        error( 'Error:', intf, 'has an IP address,'
               'and is probably in use!\n' )
        exit( 1 )

if __name__ == '__main__':
    setLogLevel( 'info' )

    # try to get hw intf from the command line; by default, use eth1 and eth2
    #intfName = sys.argv[ 1 ] if len( sys.argv ) > 1 else 'eth6' # switch to flowvisor
    #intfName2 = sys.argv[ 2 ] if len( sys.argv ) > 1 else 'eth4' # controller to switch
    #print intfName, intfName2
    #intfName3 = sys.argv[ 3 ] if len( sys.argv ) > 1 else 'eth1'
    #info( '*** Connecting to hw intf: %s, %s, %s' % (intfName,intfName2,intfName3) )
    eths = ['eth1', 'eth2', 'eth3', 'eth4', 'eth5', 'eth6']
    #info( '*** Checking', intfName, '\n' )
    for eth in eths:
        checkIntf(eth)
    #info( '*** Checking', intfName2, '\n' )

    net = Mininet(topo=ControlTopo())
    switch1 = net.switches[0]
    switch2 = net.switches[1]
    switch3 = net.switches[2]
    switch4 = net.switches[3]
    switch5 = net.switches[4]
#    switch6 = net.switches[5]

    _intf1 = Intf(eths[0], node=switch1 )
    _intf2 = Intf(eths[1], node=switch2 )
    _intf3 = Intf(eths[2], node=switch3 )
    _intf4 = Intf(eths[3], node=switch4 )
    _intf5 = Intf(eths[4], node=switch5 )
    _intf6 = Intf(eths[5], node=switch3 )
			

    info( '*** Note: you may need to reconfigure the interfaces for '
          'the Mininet hosts:\n', net.hosts, '\n' )

    net.start()
    print 'network started'
    #while (True):
	#pass
    CLI( net )
    net.stop()
