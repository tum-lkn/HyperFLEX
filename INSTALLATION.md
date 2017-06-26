# Configuration of the setup and HyperFLEX installation

## System Requirements

## Installation and dependacies 

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

## Using HyperFLEX and the configured setup 

Current HyperFLEX demo is realized on two PCs, eg. PC1 and PC2. 

PC1 contains 3 VMs:

* VM1 - Emulation of data topology using Mininet  
* VM2 - Hypervisor (i.e. flowvisor)
* VM3 - HyperFLEX 

PC2 contains:

* VM4 - Management Switch
* GUI
* SDN Controllers

## Configuration of PC-1

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