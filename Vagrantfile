# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!


# This uses Vagrant Cloud for simplicity so it needs to have Vagrant 1.5
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.provision "shell", path: "resources/puppet/scripts/bootstrap.sh"

  config.vm.provision "puppet" do |puppet|
      puppet.hiera_config_path = "resources/puppet/hiera.yaml"
      puppet.working_directory = "/vagrant/resources/puppet"
      puppet.manifests_path = "resources/puppet/manifests"
      puppet.manifest_file  = "base.pp"
  end

  # Install single host with mininet and ODL 

  config.vm.define "scipass" do |scipass|
    scipass.vm.box = "ubuntu/trusty64"
    scipass.vm.hostname = "scipass"
    scipass.vm.network "private_network", ip: "192.168.50.70"
    scipass.vm.provider :virtualbox do |vb|
      vb.memory = 4096
    end
    scipass.vm.provider "vmware_fusion" do |vf|
      vf.vmx["memsize"] = "4096"
    end
    scipass.vm.provision "puppet" do |puppet|
      puppet.hiera_config_path = "resources/puppet/hiera.yaml"
      puppet.working_directory = "/vagrant/resources/puppet"
      puppet.manifests_path = "resources/puppet/manifests"
      puppet.manifest_file  = "scipass.pp"
    end
  end
end