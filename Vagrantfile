# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!


# This uses Vagrant Cloud for simplicity so it needs to have Vagrant 1.5
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.provision "shell", path: "resources/puppet/scripts/bootstrap.sh"

  config.ssh.username      = "ubuntu"
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
    # By default points to HP Public Cloud
    # To work on HP Public Cloud or other provider that uses regions
    # vagrant-openstack-provider >=0.6.0 for OpenStack region support
    scipass.vm.provider :openstack do |os|
      os.openstack_auth_url = "#{ENV['OS_AUTH_URL']}/tokens"
      os.username           = "#{ENV['OS_USERNAME']}"
      os.password           = "#{ENV['OS_PASSWORD']}"
      os.tenant_name        = "#{ENV['OS_TENANT_NAME']}"
      os.region             = "#(ENV['OS_REGION_NAME'])"
      os.flavor             = 'standard.medium'
      os.image              = 'Ubuntu Server 14.04.1 LTS (amd64 20140927) - Partner Image'
      os.floating_ip_pool   = 'public'
      os.openstack_compute_url = 'https://region-b.geo-1.compute.hpcloudsvc.com/v2/10383253329549'
    end
    # Start VM on AWS
    #scipass.vm.provider =

    scipass.vm.provision "puppet" do |puppet|
      puppet.hiera_config_path = "resources/puppet/hiera.yaml"
      puppet.working_directory = "/vagrant/resources/puppet"
      puppet.manifests_path = "resources/puppet/manifests"
      puppet.manifest_file  = "scipass.pp"
    end
  end
end