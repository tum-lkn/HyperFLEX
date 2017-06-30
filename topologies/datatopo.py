"""Custom topology example

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        leftHost = self.addHost( 'h1' )
        rightHost = self.addHost( 'h2' )
        print type(rightHost)
        lefterHost = self.addHost( 'h3', ip='10.0.1.1')
        righterHost = self.addHost( 'h4', ip='10.0.1.2')

        leftSwitch = self.addSwitch( 's3' )
        rightSwitch = self.addSwitch( 's4' )

        # Add links
        self.addLink( rightSwitch, leftSwitch )
        self.addLink( leftHost, leftSwitch )
        self.addLink( lefterHost, leftSwitch )
        self.addLink( rightSwitch, righterHost )
        self.addLink( rightSwitch, rightHost )


class OurTopo(Topo):

    def __init__(self):
        Topo.__init__(self)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s8 = self.addSwitch('s8')

        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h5 = self.addHost('h5', ip='10.0.0.5')
        h6 = self.addHost('h6', ip='10.0.0.6')
        h8 = self.addHost('h8', ip='10.0.0.8')

        h21 = self.addHost('h21', ip='10.0.2.1')
        h22 = self.addHost('h22', ip='10.0.2.2')
        h23 = self.addHost('h23', ip='10.0.2.3')
        h25 = self.addHost('h25', ip='10.0.2.5')
        h26 = self.addHost('h26', ip='10.0.2.6')
        h28 = self.addHost('h28', ip='10.0.2.8')

        h11 = self.addHost('h11', ip='10.0.1.1')
        h12 = self.addHost('h12', ip='10.0.1.2')

        self.addLink(s4, s1)
        self.addLink(s4, s2)
        self.addLink(s4, s3)
        self.addLink(s4, s5)
        self.addLink(s4, s6)
        self.addLink(s4, s8)
        self.addLink(s1, s2)

        self.addLink(s1, h1)
        self.addLink(s2, h2)
        self.addLink(s3, h3)
        self.addLink(s5, h5)
        self.addLink(s6, h6)
        self.addLink(s8, h8)

        self.addLink(s1, h21)
        self.addLink(s2, h22)
        self.addLink(s3, h23)
        self.addLink(s5, h25)
        self.addLink(s6, h26)
        self.addLink(s8, h28)

        self.addLink(s8, h11)
        self.addLink(s8, h12)


topos = { 'mytopo': ( lambda: MyTopo() ) , 'datatopo': (lambda: OurTopo())}
