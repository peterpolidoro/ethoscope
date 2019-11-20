The original documentation from gilestro lab is located: https://qgeissmann.gitbooks.io/ethoscope-manual/building-and-installation/node.html?q= 

# This is a documentation for using the Ubuntu 16.04 instead of ArchLinux and using Janelia SW/HW setup 

# author: Salma Elmalaki 
 

Installing extra packages
--------------------------
* sudo apt update
* sudo apt install build-essential git gfortran rsync fping wget
* sudo apt install ntp bash-completion openssh-server
* sudo apt install dnsmasq
* sudo apt install python-pip python-numpy python-bottle python-serial python-cherrypy python-netifaces python-mysqldb python-future python-mysql.connector 
* sudo apt install libmysqlclient-dev 
* sudo apt install mariadb-server mariadb-client
* sudo apt install libev-dev 


Creating a git bare repo
------------------------
We are using the Janelia version of the ethoscope project which is hosted on SciCompSoft github 

* UPSTREAM_GIT_REPO=https://github.com/JaneliaSciComp/ethoscope.git
* LOCAL_BARE_PATH=/srv/git/ethoscope.git
* sudo mkdir -p /srv/git
* sudo git clone --bare $UPSTREAM_GIT_REPO $LOCAL_BARE_PATH


The node software
------------------

* TARGET_UPDATER_DIR=/opt/ethoscope_updater
* TARGET_GIT_INSTALL=/opt/ethoscope-git


* sudo git clone $LOCAL_BARE_PATH $TARGET_GIT_INSTALL

* cd $TARGET_GIT_INSTALL
* cd $TARGET_GIT_INSTALL/node_src
* sudo pip2 install -e .

* sudo ln -s $TARGET_GIT_INSTALL/scripts/ethoscope_updater $TARGET_UPDATER_DIR

Network
-------
On the router table make sure that you reserve the address 192.168.123.2 for the server node. 
Reboot the router to detect the new MAC address  
* You can get the MAC address of the server node using ifconfig 
* You can access the network configuration from: http://www.routerlogin.com/
* You will need to reset the credentials to change the configurations of the LAN 
* On the router page you go to Basic--Attached Devices, then you will see all the IPs assigned from this router to the different RPis
* On the router page you go to Advanced--Setup--LAN Setup, then you will see the static IPs 


DNS
----
* NODE_IP=192.168.123.2
* Get the interface for the node ip from ifconfig 
* echo "interface=ep0s25">>/etc/dnsmasq.conf
* echo "dhcp-option = 6,$NODE_IP" >> /etc/dnsmasq.conf 
* echo "no-hosts" >> /etc/dnsmasq.conf
* echo "addn-hosts=/etc/hosts" >> /etc/dnsmasq.conf
* echo "$NODE_IP node" >> /etc/hosts

System Daemons
--------------

* systemctl start ntp.service
* systemctl enable ntp.service
* systemctl enable ssh.service
* systemctl start ssh.service


Our own daemons
---------------

* cd $TARGET_GIT_INSTALL/scripts

* sudo cp ./ethoscope_node.service /etc/systemd/system/ethoscope_node.service
* sudo cp ./ethoscope_backup.service /etc/systemd/system/ethoscope_backup.service
* sudo cp ./ethoscope_video_backup.service /etc/systemd/system/ethoscope_video_backup.service
* sudo cp ./ethoscope_git_daemon.service /etc/systemd/system/ethoscope_git_daemon.service

* sudo systemctl daemon-reload

* sudo systemctl enable ethoscope_node.service
* sudo systemctl enable ethoscope_backup.service
* sudo systemctl enable ethoscope_video_backup.service
* sudo systemctl enable ethoscope_git_daemon.service

* cd $TARGET_UPDATER_DIR
* sudo cp ethoscope_update_node.service /etc/systemd/system/ethoscope_update_node.service

* sudo systemctl daemon-reload
* sudo systemctl enable ethoscope_update_node.service


Time
----
* timedatectl set-timezone GMT

In order to allow the node to server time regardless, you can add these two lines to /etc/ntp.conf:

* server 127.127.1.1
* fudge 127.127.1.1 stratum 12


What is next
------------
In order to check things:

* Reboot the computer
* Open your browser (chrome)
* Test the local server at http://0.0.0.0:8000

* Test the update server http://0.0.0.0:8888

* Troubleshooting:  You can check that the services are running by: sudo systemctl status $name.service 

* For database veiwer: sudo apt install sqlitebrowser



