# HyperFLEX installation and Configuration of example setup

## System Requirements & Overall Setup

The provided example setup of HyperFLEX uses two PCs and in total 5/6 VMs. Hence, it is advised to have a sufficient amount of CPUs and RAM per PC (e.g. at least 4CPUs and at least 8GB per PC).

Testing was done on ubuntu 14.04, hence, it is advised to use this version for VMs.

PC1 contains:

* VM1 - HyperFLEX Framework
* VM2 - Hypervisor (i.e. flowvisor) and monitoring agent
* VM3 - Emulation of data topology using Mininet 

PC2 contains:

* VM4 - Management Switch
* HyperFLEX GUI
* SDN Controllers (typically one per VM)

**After** completion of the installation process, two PCs should be **connected** and assigned static IPs, PC-1 '10.162.149.123/16' and PC-2 '10.162.149.125/16'. 

If you wish to use real network instead of mininet or a different setup, different configuration of the interfaces will be necessary.

## Configuration of PC-1

### Installation of HyperFLEX and all dependacies - VM1

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

Pull [HyperFLEX](https://github.com/tum-lkn/HyperFLEX) from git.


Add an mysql user "user" without a password and enable the external access to the databases. Then, import a MySQL database "database/database_clean.sql"   

Add one bridged interface to the VM with a static IP of 10.162.149.124/16.

HyperFLEX framework can be run as:

```
cd HyperFLEX/hyperflexcomplete/hyperflexcore
python -m hypeflexcore.guicontroller.guicontroller
```

### Hypervisor Setup - VM2

Install dependancies:
```
sudo apt-get install python-pip python-dev build-essential libtool
sudo pip install json-rpc
sudo apt-get install python-psutil
```
You will also need to install [nanomsg](https://github.com/nanomsg/nanomsg) from source, and `sudo pip install nanomsg`. 

As well as [flowvisor](https://github.com/OPENNETWORKINGLAB/flowvisor/wiki/Installation-from-Binary) and pull [HyperFLEX](https://github.com/tum-lkn/HyperFLEX).

Add 3 network interfaces to VM, one internal interface 'mn-hv' to the mininet with ip 192.168.125.20/24 and two bridged, one for control plane traffic and one for management as:

* eth2 (bridging eth0) with static ip 10.162.149.241/24
* eth3 (bridging eth0) with static
    * address 192.168.200.100
    * netmask 255.255.254.0
    * up route add -net 192.168.50.0/24 dev eth3
    * up route add -net 192.168.75.0/24 dev eth3  

Run flowvisor (i.e. `sudo -u flowvisor flowvisor`), and run the monitoring agent:
```
python HyperFLEX/hyperflexcomplete/hyperflexcore/hyperflexcore/data/livedata.py --sufix=1
```
### Setup of Emulated Data topology - VM3

Install [mininet](http://mininet.org/) and download topologies/datatopo.py.

Add to mininet VM - VM3 one internal interface (this interface is used for a connection to the hypervisor) 'mn-hv' and set up a static ip 192.168.125.21/24 and run the topo as:
```
sudo -mn --controller=remote,ip=192.168.125.20,port=6633 --custom HyperFLEX/topologies/datatopo.py --topo datatopo
```  


## Configuration of PC-2

Configure it with a static IP of 10.162.149.125/16 after completing installation.

### Management switch VM-4

Management switch is providing control plane topology. Furthermore, to provide control to the HyperFLEX one listening agent in necessary. Hence, following dependencies are needed:
```
mininet
sudo pip install json-rpc
sudo pip install werkzeug
```

Also get HyperFLEX from github.

Management switch is providing interfaces to controllers, hence, it needs a few internal interfaces. The VM should contain 7 adapters, where Adapter 1 & Adapter 7 are configured as bridged, while the rest (Adapter 2-6) should be internal and they should be named as Adapter 2 - 'ctrl-sw-1', Adapter 3 - 'ctrl-sw-2'.

Networking configuration (`gedit /etc/network/interfaces`) should look like:
```
auto eth0
iface eth0 inet static
address 10.162.149.240
netmask 255.255.254.0

auto eth1
iface eth1 inet manual
up ifconfig eth1 up
```

Other interfaces should be configured the same as eth1.

After installation and configuration of interfaces it is possible to run the switch as:
```
sudo python HyperFLEX/topologies/controltopo.py
python -m hyperflexcore.management.rpcserver
sudo ./HyperFLEX/topologies/init_switch_rules 
```

### SDN Controllers

The SDN controllers should be placed in VMs with static IPs and internal network adapter configured as one of the options:
1) Internal network 'ctrl-sw1' with static IP 192.168.75.10/24 
2) Internal network 'ctrl-sw4' with static IP 192.168.50.10/24



### GUI setup

Pull [HyperFLEX GUI](https://github.com/tum-lkn/HyperFLEX/).

To open **Tenant View GUI** open `HyperFLEX/hyperflexcomplete/hyperflexgui/html/tenant/tenant_gui.html` and use username 'tenant1' and password 'tenant'.

To open **HyperFLEX Core GUI** open `HyperFLEX/hyperflexcomplete/hyperflexgui/html/hyperflex/hypervisor_gui.html`.

To open **Monitoring GUI** open `HyperFLEX/hyperflexcomplete/hyperflexgui/html/monitoring/index.html`.