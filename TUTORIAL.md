# HyperFLEX TUTORIAL

In this tutorial it is presented how to use HyperFLEX GUI, and how to add and run simple virtual SDN networks.

Follow the instructions from [Installation](https://github.com/tum-lkn/HyperFLEX/INSTALLATION.md) to configure provided example setup.

## Tenant View GUI

_Disclaimer:_ Following fields in **Tenant View GUI** are not used:

* Node Info: Name, Ports, vSDN, CPU
* Edge Info: VSDN, Connected, Bandwidth.

In the current setup, each controller in every city is assumed to be connected to a certain interface on a management switch. Hence, when adding the controller the interface and IP has to match. 

### Adding a first VSDN

In the _UPPER RIGHT_ corner under 'VSDNs' click on the button '+New VSDN'.

Fill out filed under 'Network Parameters' as:

* VSDN Name: e.g. 'VSDN1' 
* Controller IP/port: 192.168.75.10 
* Subnet: '10.0.0.0/16' - hosts in Mininet topo are on this subnet 
* Isolation Method: Check 'Software' 
* Control msg rate: '1000' 

_Adding nodes_: In the left part of the screen click on the blue icon of 'Hamburg', afterwards, on the right side, under the filed name 'Node Info' click on the '+Add Node to VSDN'. Add city of 'Dresden' in the similar fashion. 

_Adding edge_: Under the field 'Control' select 'Add Edge'(In case 'Control' is not fully seend, minimize the 'Network Parameters'), click on the city of Dresden and swipe the edge to Hamburg.

_Adding a controller_: Under the field 'Control' select 'Add Node', and fill in following fields as:

* Node type: 'Ctrl'
* Attributes: check 'Control Plane'
* Label: 'c1'
* Entry Point: 'CTRL_HAMBURG'
* Click on 'Add'.

Network is now ready to be requested by clicking on the 'Request VSDN' under 'Control'.

Run the desired SDN controller in VM with internal network interface 'ctrl-sw-4' with a static IP 192.168.75.10/24 to control your vSDN. 

If you wish to update isolation method or rate, first click in the tenant view under 'VSDNs' on the network you wish to edit, afterwards, edit the parameters and select 'Update VSDN'.

If you wish to add a second vSDN it is just necessary to specify a host and a controller at Berlin with IP 192.168.50.10/24 and to connect the VM containing the controller to 'ctrl-sw-1'. 

### HyperFLEX Core GUI

_Disclaimer:_ Only _Receive Topology_ and _Receive VSDNs_ are used in this GUI, furthermore, the CPU resource reservation is calculated based on the offline measurements, hence, it might not be accurate for every platform. 

Infrastructure GUI view provides the overlook of the whole network from the perspective of a provider. 

### Monitoring GUI.

_Disclaimer:_ For control plane monitoring, i.e. latency and drop rate in **Monitoring GUI**, HyperFLEX uses PerfBench control packet generator, which is not yet released!

Hence, this GUI provides only monitoring of the current utilization of hypervisor CPU.
