# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "hashicorp/precise32"

  config.vm.network "forwarded_port", guest: 6667, host: 6667

  # config.vm.network "private_network", ip: "192.168.42.7"
  # config.vm.network "istic_networks"

  config.ssh.forward_agent = true

  # config.vm.provider "virtualbox" do |vb|
  #   # Don't boot with headless mode
  #   vb.gui = true
  #
  #   # Use VBoxManage to customize the VM. For example to change memory:
  #   vb.customize ["modifyvm", :id, "--memory", "1024"]
  # end


  config.vm.provision :shell, :path => "deploy/dev/vagrant_provision.sh"
  config.vm.provision :shell, :path => "deploy/dev/vagrant_update.sh", run: "always"

end
