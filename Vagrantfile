# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-16.04-i386"
  config.vm.box_version = "= 2.3.5"
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Work around disconnected virtual network cable.
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--cableconnected1", "on"]
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get -qqy update

    # Work around https://github.com/chef/bento/issues/661
    # apt-get -qqy upgrade
    DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade

    #apt-get -qqy install make zip unzip postgresql

    apt-get -qqy install python python-pip
    pip install --upgrade pip
    pip install flask==0.9
    pip install SQLAlchemy==1.0.7
    pip install flask-seasurf==0.1.21

    pip install httplib2 oauth2client psycopg2 requests

    #su postgres -c 'createuser -dRS vagrant'
    #su vagrant -c 'createdb'
    #su vagrant -c 'createdb news'

    vagrantTip="[35m[1mThe shared directory is located at /vagrant\\nTo access your shared files: cd /vagrant[m"
    echo -e $vagrantTip > /etc/motd

    echo "Done installing your virtual machine!"
  SHELL
end
