The original documentation from gilestro lab is located: https://qgeissmann.gitbooks.io/ethoscope-manual/building-and-installation/node.html?q= 

# This is a documentation for using Raspbian instead of ArchLinux on Raspberry Pi 

# author: Salma Elmalaki 


Install Raspbian OS image using the following instruction 
https://www.raspberrypi.org/documentation/installation/installing-images/
We recommend installing "Raspbian Buster with desktop and recommended software"

Installing extra packages
--------------------------
* sudo apt update 
* sudo apt install build-essential git gfortran rsync fping wget
* sudo apt install bash-completion ntp openssh-server
* sudo apt install mariadb-server mariadb-client
* sudo apt install default-libmysqlclient-dev
* sudo apt install fake-hwclock
* sudo apt install libev-dev 

If you’re working with a fresh install of the OS, it is possible that these versions of Python are already at the newest version (you’ll see a terminal message stating this).
Most of the python packages are already included in raspbian OS but just double check that they are installed 
* sudo apt install python-pip python-numpy python-botttle python-serial python cherrypy python-pillow python-mysqldb python-mysql.connector python-scipy 
* sudo apt install modular_client


Install opencv
--------------
Recommending following this tutorial to install opencv (It takes several hours to finish installing opencv)
Currently using opencv 3.4.3.
https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/

Don't use virtual environment. 

In Step#5 in the tutorial add the following to the cmake -D ENABLE_CXX11=ON  

You can skip Step#6 because we don't use virtual environment 

Environment Environment variables
----------------------------------

Here we define a few variables used in the rest of the installation

mysql credentials

* USER_NAME=ethoscope
* PASSWORD=ethoscope
* DB_NAME=ethoscope_db

where ethoscope saves temporary local files (e.g. videos)

* DATA_DIR=/ethoscope_data

where to install and find our software

* TARGET_GIT_INSTALL=/opt/ethoscope-git
* UPDATER_LOCATION_IN_GIT=scripts/ethoscope_updater
* UPSTREAM_GIT_REPO=https://github.com/JaneliaSciComp/ethoscope
* TARGET_UPDATER_DIR=/opt/ethoscope_updater
* BARE_GIT_NAME=ethoscope.git

network stuff

* NETWORK_SSID=ETHOSCOPE_WIFI
* NETWORK_PASSWORD=ETHOSCOPE_1234

ip addresses
* NODE_SUBNET=192.168.123
* NODE_IP=$NODE_SUBNET.2


NTP
---
modify /etc/ntp.conf 

Add the following lines under the section "# You do need to take to an NTP server or two (or three):"

* server 192.168.123.2
* server 127.127.1.0
* fudge 127.127.1.0 stratum 10

Add the following lines at the end of the file 

* restrict default kod limited nomodify nopeer noquery notrap
* restrict 127.0.0.1
* restrict ::1

Network Daemons
---------------
Enable networktime protocol

* systemctl start ntp.service
* systemctl enable ntp.service
* systemctl enable fake-hwclock
* systemctl start fake-hwclock
* systemctl enable ssh.service
* systemctl start ssh.service


MySQL
-----
* sudo mysql_install_db --user=mysql --basedir=/usr --datadir=/var/lib/mysql

(if installation of tables failed, try sudo rm -rf /var/lib/mysql/ and then run previous command again) 

* sudo systemctl start mysql.service
* sudo systemctl enable mariadb.service
* sudo mysql -u root -e "CREATE USER \"$USER_NAME\"@'localhost' IDENTIFIED BY \"$PASSWORD\""
* sudo mysql -u root -e "CREATE USER \"$USER_NAME\"@'%' IDENTIFIED BY \"$PASSWORD\""
* sudo mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO \"$USER_NAME\"@'localhost' WITH GRANT OPTION";
* sudo mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO \"$USER_NAME\"@'%' WITH GRANT OPTION";
* sudo mysql -u root -e "FLUSH PRIVILEGES";

Add the following lines in  /etc/mysql/my.cnf 

[mysqld]
 
skip-name-resolve
innodb_buffer_pool_size = 128M
innodb_log_file_size = 32M
innodb_log_buffer_size = 50M
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50
innodb_file_per_table=1
innodb_file_format=Barracuda

In file /etc/mysql/mariadb.conf.d/50-server.conf comment the line "bind-address  127.0.0.1" and uncomment the line "log_bin = /var/log/mysql/mysql-bin.log"

Restart the services:
* sudo systemctl restart mariadb.service
* sudo systemctl restart mysql.service 

Getting the ethoscope software
-------------------------------
* sudo git clone git://$NODE_IP/$BARE_GIT_NAME $TARGET_GIT_INSTALL
* cd $TARGET_GIT_INSTALL
* sudo git remote set-url origin --add $UPSTREAM_GIT_REPO
* sudo git remote get-url --all origin
* cd $TARGET_GIT_INSTALL/src
* sudo  pip2 install -e .[device]

Ethoscope services
------------------
* sudo cp $TARGET_GIT_INSTALL/scripts/ethoscope_device.service /etc/systemd/system/ethoscope_device.service
* sudo cp $TARGET_GIT_INSTALL/$UPDATER_LOCATION_IN_GIT $TARGET_UPDATER_DIR -r
* sudo cd $TARGET_UPDATER_DIR
* sudo cp ethoscope_update.service /etc/systemd/system/ethoscope_update.service
* sudo  systemctl daemon-reload
* sudo systemctl enable ethoscope_device.service
* sudo systemctl enable ethoscope_update.service

Boot config file
-----------------
* echo 'gpu_mem=256' >> /boot/config.txt
* echo 'start_x=1' >> /boot/config.txt

Make sure the camera is enabled: Go into the Raspberry Pi Configuration tool (sudo raspi-config), click Interfaces, and select Enabled beside the Camera option.

Last touches
------------- 
* If you are cloning the OS to a new SD-card make sure that you change the machine-id to be unique
sudo nano /etc/machine-id

* Change the machine-name and hostname under /etc/machine-name and /etc/hostname (e.g. ETHOSCOPE_001) and  (e.g. e001) 

* Use the same hostname you chose to change the entry of 127.0.1.1 in /etc/hosts

* Change the datetime on the pi to be UTC. run sudo raspi-config and With Localisation Options open you'll be able to choose Change Timezone and select your local timezone.

