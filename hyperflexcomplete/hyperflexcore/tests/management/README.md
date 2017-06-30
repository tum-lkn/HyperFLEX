# How to test flowvisor
To test flowvisor capabilities you need to set up some stuff.

What you need is (easiest is one) VM with the following tools:

- flowvisor (naturally)
- mininet
- OpenFlow Controller

To expose flowvisor to the outside, adapt its startup config located in
`/etc/flowvisor/config.json` and change the ip address in the config file
to the one of your virtual machine. Alternatively you can also create another
custom config file and start flowvisor with that one (check fvctl help).

You could also change the defined port, but it is not necessary.

Ok, if that is done, start mininet with whatever topology you want. But do so
with a remote controller and, guess what, the controller is flowvisor and
you are not going to believe it, but the ip and port for the remote controller
are the ones in the `/etc/flowvisor/config.js`.

The easiest (creates one switch with two hosts connected) is:

```
sudo mn --controller=remote,ip=<flowvisor_ip>,port=<flowvisor_port>
```

If you want to check connectivity between you hosts you can do it now. Will not
matter though since I promise you its not going to work (if it does, check
what slices and flowspaces are defined for you flowvisor).

Next up is you controller. The controller will be used for the slices (in the 
testcases I am assuming localhost). Soo if you are not using localhost, you
have to adapt the testcases so they work.

