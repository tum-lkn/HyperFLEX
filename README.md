# HyperFLEX - About

**IN DEVELOPMENT AND CURRENTLY IS BEING ADDED TO GITHUB**

Framework for Virtualization of SDN Environments.

Current Version - 1.0 Beta Release (26. June 2017).

HyperFlex splits the SDN hypervisor into functions, that could be hosted by servers or SDN network elements. The main goal is to provide an adaptable SDN hypervisor layer, with respect to the requirements of the virtual SDN (vSDN) tenants, state of the SDN physical infrastructure and the resources to host the hypervisor layer. 

HyperFLEX framwork relies on external hypervisor (e.g. flowvisor), and additionaly it provides additional features:

* **Management System** - Every tenant is able to request a virtual network with specific network parameters, while the infrastructure provider can overlook the whole system.
* **Monitoring Agents** - Most important resources, such as Hypervisor CPU, control plane delay and loss are monitored at all times. 
* **Software & Hardware CPU Isolation of Control Plane** - Tenant is allowed to used only the amount of resources he requested.
* **Admission Control** - If there are no available resources, the request for a new virtual network will be rejected.

Configuration of the example set-up and installation of HyperFLEX can be found in the file [INSTALLATION.md](https://github.com/tum-lkn/HyperFLEX/INSTALLATION.md), and tutorial for using HyperFLEX and HyperFLEX GUI can be found in the file [TUTORIAL.md](https://github.com/tum-lkn/HyperFLEX/TUTORIAL.md). List of version and details about them are stored in [RELEASE-NOTES.md](https://github.com/tum-lkn/HyperFLEX/RELEASE-NOTES.md).

Collection of HyperFLEX related publications can be found at [PUBLICATIONS.txt](https://github.com/tum-lkn/HyperFLEX/PUBLICATIONS.txt).

# Project and Code Structure

TODO: Add a picture from wiki here

## Package data 

Contains everython related to reading/writing to database. It uses _storm_ to connect to RDBMS. _Storm_ is an Object-Relational Mapper developed by Canonical.

## Package guicontroller 

Contains interfaces for GUIs to connect to. JSON RPC is used as a protocol. The main task of this package is handling the connections and parasing/serializing messages into specific formats (serialize it to whatever the GUI wants, parase what the GUI sends so that the rest of components of this project understand it).

## Package Intelligence

Contains modules for handling requsts made through GUI. Ii also hosts actual intelligence, like fining embeddings, autonomously set rates and so on.

## Package managements 

Interface to distributed components like Hypervisor and network controller of vSDN (at the moment and OVS, but should actually be another controller). Also uses JSON RPC to communicate with components. Main objective of this package is to provide outbound interfaces to query distributed state or issue commands. Parase replies of components so that the other modules can understand it.

