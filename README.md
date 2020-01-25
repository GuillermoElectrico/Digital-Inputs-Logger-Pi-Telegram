# Digital-Inputs-Logger-Pi
Log inputs status on a Raspberry Pi and if change value send mesagge to telegram.
Its been verified to work with a raspberry pi with simple 13 inputs module (Included in PCB folder). By changing the inputs_pins_message.yml file and making a corresponding GPIO inputs relation.

### Requirements

#### Hardware

* Raspberry Pi B+
* 13 inputs module (Included in PCB folder) or other module DIY

#### Software

* Raspbian or dietpi
* Python 3.4 and PIP3
* [RPi.GPIO](https://pypi.org/project/RPi.GPIO/)


### Installation

#### Install Digital-Inputs-Logger-Pi-Telegram:
* Download and install from Github and install pip3
    ```sh
	$ sudo apt-get install git
    $ git clone https://github.com/GuillermoElectrico/Digital-Inputs-Logger-Pi.Telegram.git
	$ sudo apt-get install python3-pip
    ```
* Run setup script (must be executed as root (sudo) if the application needs to be started from rc.local, see below)
    ```sh
    $ cd Digital-Inputs-Logger-Pi-Telegram
    $ sudo python3 setup.py install
    ```    
* Make script file executable
    ```sh
    $ chmod 777 read_input_raspberry.py
    ```
* Edit inputs.yml to match your configuration and influx_config.yml
* Test the configuration by running:
    ```sh
    ./read_input_raspberry-telegram.py
    ./read_input_raspberry-telegram.py --help # Shows you all available parameters
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
    /home/pi/Digital-Inputs-Logger-Pi-Telegram/read_input_raspberry-telegram.py > /var/log/inputs-logger-telegram.log &
    ```
	
    Log with potential errors are found in /var/log/inputs-logger-telegram.log
