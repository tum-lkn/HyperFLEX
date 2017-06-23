# HyperFLEX
Framework for Virtualization of SDN Environments, **IN DEVELOPMENT AND CURRENTLY ADDING TO GITHUB**.

HyperFLEX framwork relies on external hypervisor (e.g. flowvisor), and additionaly it provides additional features:

* Management System
* Monitoring Agents
* Software & Hardware CPU Isolation of Control Plane
* Admission Control

#Structure 

## Package data 

Contains everython related to reading/writing to database. It uses _storm_ to connect to RDBMS. _Storm_ is an Object-Relational Mapper developed by Canonical.

## Package guicontroller 

Contains interfaces for GUIs to connect to. JSON RPC is used as a protocol. The main task of this package is handling the connections and parasing/serializing messages into specific formats (serialize it to whatever the GUI wants, parase what the GUI sends so that the rest of components of this project understand it).

## Package Intelligence

Contains modules for handling requsts made through GUI. Ii also hosts actual intelligence, like fining embeddings, autonomously set rates and so on.

## Package managements 

Interface to distributed components like Hypervisor and network controller of vSDN (at the moment and OVS, but should actually be another controller). Also uses JSON RPC to communicate with components. Main objective of this package is to provide outbound interfaces to query distributed state or issue commands. Parase replies of components so that the other modules can understand it.

# Installation and dependacies 

Testing was done on Ubuntu 14.04, using a VM is advised, and the following packages are required:

```
#General purpose and MySQL database
sudo apt-get install autoconf build-essential pkg-config libevent-dev libssl-dev libcap-dev libboost-all-dev python-dev libtool git
sudo apt-get install mysql-server
sudo apt-get install mysql-client
sudo apt-get install mysql-workbench
sudo apt-get install libmysqlclient-dev python-mysqldb
sudo apt-get install python-pip
sudo pip install json-rpc

#Dependancies
sudo apt-get install python-storm
sudo pip install trollius
sudo pip install autobahn==0.17.1
sudo pip install json
sudo pip install werkzeug
sudo pip install networkx
sudo pip install numpy
sudo apt-get install python-scipy
sudo pip install scikit-learn
sudo apt-get install python-psutil
sudo pip install docopt
```

You will also need to install [nanomsg](https://github.com/nanomsg/nanomsg) from source, as well as `sudo pip install nanomsg`.

Before starting up, import a MySQL database "database_clean.sql". Also, add an mysql user "user" without a password and enable the external access to the databases.   

# Using HyperFLEX and the configured setup 

Current HyperFLEX demo is realized on two PCs, eg. PC1 and PC2. 

PC1 contains 3 VMs:

* VM1 - Emulation of data topology using Mininet  
* VM2 - Hypervisor (i.e. flowvisor)
* VM3 - HyperFLEX 

PC2 contains:

* VM4 - Management Switch
* GUI
* SDN Controllers

##Configuration of PC-1

### Setup of Emulated Data topology - VM1

Install [mininet](http://mininet.org/) and pull data_topo_scripts/datatopo.py.

Add to VM1 one internal interface 'mn-hv' and set up a static ip 192.168.125.21/24 and run the topo as:
```
sudo -mn --controller=remote,ip=192.168.125.20,port=6633 --custom /datatopo.py --topo datatopo
```  

### Hypervisor Setup - VM2

Install dependancies:
```
sudo apt-get install python-pip python-dev build-essential libtool
sudo pip install json-rpc
```
You will also need to install [nanomsg](https://github.com/nanomsg/nanomsg) from source, as well as `sudo pip install nanomsg`. 

As well as [flowvisor](https://github.com/opennetworkinglab/flowvisor) and pull hypeflexcore.

Add one internal interface 'mn-hv' to the mininet with ip 192.168.125.20/24 and two bridged, one for control plane traffic and one for management as:

* eth2 (bridging eth0) with static ip 10.162.149.241/24
* eth3 (bridging eth0) with static
    * ip 192.168.200.100
    * netmask 255.255.254.0
    * up route add -net 192.168.50.0/24 eth3
    * up route add -net 192.168.75.0/24 eth3  

Or just use our VM image:.  

Run flowvisor (i.e. `sudo -u flowvisor flowvisor`), and run the monitoring agent:
```
python hyperflexcore/hyperflexcore/data/livedata.py --sufix=1
```

### Setup of HyperFLEX

Installation was explained in previous sections, it is just needed to add one bridged interface to the VM containing the HyperFLEX with static IP of 10.162.149.124/16.


## Configuration of PC-2

Configure it with a static IP of 10.162.149.125/16 after pulling all the stuff.

### Management switch VM-4

To avoid configuring interfaces, pull the VM image from link and import it.

To run the switch, just boot up the VM.

The SDN controllers should be placed in VMs with static IPs and internal network adapter configured as one of the options:
1) Internal network 'ctrl-sw1' with static IP 192.168.75.10 
2) Internal network 'ctrl-sw4' with static IP 192.168.50.10

### GUI setup

Pull HyperFLEX GUI from hyperflexgui.

To open **Tenant View GUI** open `/hyperflexcomplete/hyperflexgui/html/tenant/tenant_gui.html` and use username 'tenant1' and password 'tenant'.

To open **HyperFLEX Core GUI** open `/hyperflexcomplete/hyperflexgui/html/hyperflex/hypervisor_gui.html`.

To open **Monitoring GUI** open `/hyperflexcomplete/hyperflexgui/html/monitoring/index.html`.

# Using HyperFLEX GUI & demo

## Tenant View GUI

_Disclaimer:r_ Following fields in **Tenant View GUI** are not used:

*Node Info: Name, Ports, vSDN, CPU
*Edge Info: VSDN, Connected, Bandwidth.

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

*Node type: 'Ctrl'
*Attributes: check 'Control Plane'
*Label: 'c1'
*Entry Point: 'CTRL_HAMBURG'
*Click on 'Add'.

Network is now ready to be requested by clicking on the 'Request VSDN' under 'Control'.

Run the desired SDN controller in VM with internal network interface 'ctrl-sw-4' with a static IP 192.168.75.10/24 to control your vSDN. 

If you wish to update isolation method or rate, first click in the tenant view under 'VSDNs' on the network you wish to edit, afterwards, edit the parameters and select 'Update VSDN'.

If you wish to add a second vSDN it is just necessary to specify a host and a controller at Berlin with IP 192.168.50.10/24 and to connect the VM containing the controller to 'ctrl-sw-1'. 

### HyperFLEX Core GUI

_Disclaimer:_ Only Receive Topology and Receive VSDNs are used in this GUI, furthermore, the CPU resource reservation is calculated based on the offline measurements, hence, it might not be accurate for every platform'. 

Infrastructure GUI view provides the overlook of the whole network from the perspective of a provider. 

### Monitoring GUI.

_Disclaimer:_ For control plane monitoring, i.e. latency and drop rate in **Monitoring GUI**, HyperFLEX uses PerfBench control packet generator, which is not yet released!

Hence, this GUI provides only monitoring of the current utilization of hypervisor CPU.
