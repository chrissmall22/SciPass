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

To start the Ryu version of SciPass
		
	  cd scipass/python	
	  sudo mkdir /etc/SciPass
	  sudo cp t/etc/SciPass-mininet.xml /etc/SciPass
	  ryu-manager Ryu.py


To create a Mininet network to match SciPass-mininet.xml

	  cd mininet
	  mn --controller=remote,ip=localhost 

Postman
=======
Install Postman for Chrome http://www.getpostman.com/

Add repository at scipass/resources/postman/SciPass-API.json.postman_collection

OpenDayLight
===========

To start up the OpenDaylight Controller

      cd distribution-karaf-0.2.0-Helium
      bin/karaf
