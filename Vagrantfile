#-*- mode: ruby -*-                                                                                                                                           
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2" 

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Use Ubuntu 14.04 LTS Server image
  config.vm.box = "ubuntu/trusty64"
  # Forward port 5000. Use this port to run django/flask dev server.
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  # Sync folder so its visible from outside the VM and inside
  config.vm.synced_folder ".", "/home/vagrant/dev/sesh"
  config.vm.synced_folder ".", "/vagrant", disabled: true
  # Increase default RAM to 2GB in order to run all the packages we need. 
  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--memory", 2048]
  end
  # Use Ansible to provision the VM.
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "playbook.yml"
  end 
end
