SciPass
=======

SciPass is a SDN powered Science DMZ and IDS Load Balancer. 


VM Environment with OpenDayLight
=======

The Vagrantfile provides a quick and easy way to spin up a VM containing all the code to run 
SciPass and a Mininet based test environment to test functionality.



To create the SciPass VM:

First make sure Vagrant https://www.vagrantup.com/ is installed for your OS. You will need Vagrant 1.5 to use the Vagrant Cloud boxes. You should also have Hypervisor software installed. this has been tested agqinst VirtualBox but VMWare Workstation/Fusion should work as well.

To create the VM with SciPass and ODL installed

      vagrant up
      vagrant ssh scipass

To start up the OpenDaylight Controller

      cd distribution-karaf-0.2.0-Helium
      bin/karaf

To create a 2-node Mininet network 

	  cd mininet
	  mn --controller=remote,ip=localhost 
