# Digital-Inputs-Logger-Pi
Log inputs status on a Raspberry Pi and plot graphs of your data.
Its been verified to work with a raspberry pi with simple 13 inputs module (coming soon PCB). By changing the inputspins.yml file and making a corresponding GPIO inputs relation.

### Requirements

#### Hardware

* Raspberry Pi B+
* 13 inputs module (coming soon PCB) or other module DIY

#### Software

* Raspbian or dietpi
* Python 3.4 and PIP3
* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)
* [InfluxDB](https://docs.influxdata.com/influxdb/v1.3/)
* [Grafana](http://docs.grafana.org/)

### Installation
#### Install InfluxDB*

##### Step-by-step instructions
* Add the InfluxData repository
    ```sh
    $ curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
    $ source /etc/os-release
    $ test $VERSION_ID = "10" && echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
    ```
* Download and install
    ```sh
    $ sudo apt-get update && sudo apt-get install influxdb
    ```
* Start the influxdb service
    ```sh
    $ sudo service influxdb start
    ```
* Create the database
    ```sh
    $ influx
    CREATE DATABASE db_inputs
    exit
    ```
[*source](https://docs.influxdata.com/influxdb/v1.7/introduction/installation/)

#### Install Grafana*

##### Step-by-step instructions
* Add APT Repository
    ```sh
    $ echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
    ```
* Add Bintray key
    ```sh
    $ curl https://packages.grafana.com/gpg.key | sudo apt-key add -
    ```
* Now install
    ```sh
    $ sudo apt-get update && sudo apt-get install grafana
    ```
* Start the service using systemd:
    ```sh
    $ sudo systemctl daemon-reload
    $ sudo systemctl start grafana-server
    $ systemctl status grafana-server
    ```
* Enable the systemd service so that Grafana starts at boot.
    ```sh
    $ sudo systemctl enable grafana-server.service
    ```
* Go to http://localhost:3000 and login using admin / admin (remember to change password)
[*source](http://docs.grafana.org/installation/debian/)

#### Install Digital-Inputs-Logger-Pi:
* Download and install from Github and install pip3
    ```sh
	$ sudo apt-get install git
    $ git clone https://github.com/GuillermoElectrico/Digital-Inputs-Logger-Pi.git
	$ sudo apt-get install python3-pip
    ```
* Run setup script (must be executed as root (sudo) if the application needs to be started from rc.local, see below)
    ```sh
    $ cd Digital-Inputs-Logger-Pi
    $ sudo python3 setup.py install
    ```    
* Make script file executable
    ```sh
    $ chmod 777 read_input_raspberry.py
    ```
* Edit inputs.yml to match your configuration and influx_config.yml
* Test the configuration by running:
    ```sh
    ./read_input_raspberry.py
    ./read_input_raspberry.py --help # Shows you all available parameters
    ```

	If the error appears:
	```
	/usr/bin/env: ‘python3\r’: No such file or directory
	```
	Use dos2unix to fix it.
	```
	$ sudo apt install dos2unix
	$ dos2unix /PATH/TO/YOUR/FILE
	```

* To run the python script at system startup. Add to following lines to the end of /etc/rc.local but before exit:
    ```sh
    # Start Inputs Logger
    /home/pi/Digital-Inputs-Logger-Pi/read_input_raspberry.py > /var/log/inputs-logger.log &
    ```
	
    Log with potential errors are found in /var/log/inputs-logger.log

#### Optional, Install and Configure RTC DS3231

In the case of not having internet in the installation where you have the meter with the raspberry pi, you can install an RTC DS3231 module to be able to correctly register the date and time in the database and grafana.

##### Step-by-step instructions
* First connect the RTC module
	Connect to the corresponding pins +3.3V, SDA1 (GPIO2), SCL1 (GPIO3) and GND of the raspberry pi (depending on the model, in google there are examples).  

* Enable I2C port vía raspi-config*
    ```sh
    $ sudo raspi-config
    ```
	
	Reboot after enabled.
	
	*If you use orange pi or similar, consult documentation.
	
*  Install i2c-tools and verify that the i2c bus and the RTC module are working (Optional)
    ```sh
    $ sudo apt-get install i2c-tools
	$ sudo i2cdetect -y 1
	    0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
	00:          -- -- -- -- -- -- -- -- -- -- -- -- --
	10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
	60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
	70: -- -- -- -- -- -- -- --
    ```
* Now check the time of the module, and if it is the case, update the date and time.
	
	Enable RTC module:
	```sh
    $ sudo bash
	$ echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
	$ exit
    ```
	
	With this the time is read from the RTC:
	```sh
    $ sudo hwclock -r --rtc /dev/rtc0
    ```
	
	*If you get an error or can not find /dev/rtc0, check the name of the rtc with:
	```sh
	$ ls /dev/rtc?
    ```
	
	The system time can be seen with: 
    ```sh
	$ date
	jue may  5 23:02:46 CLST 2016
	```
	
	To set the system time, this command is used:
    ```sh
	$ sudo date -s "may 5 2016 23:09:40 CLST"
	jue may  5 23:09:40 CLST 2016
    ```
	
	Now as the system clock is fine, you can set the time in the RTC as:
	```sh
    $ sudo hwclock -w --rtc /dev/rtc0
    ```


* To set the date from the rtc each time the system is started Add to following lines to the end of /etc/rc.local but before exit:
    ```sh
	$ sudo nano /etc/rc.local
	```
	
	```sh
    echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
	sleep 1
	hwclock -s --rtc /dev/rtc0
    ```