#!/usr/bin/env python3

from datetime import datetime, timedelta
from os import path
import RPi.GPIO as GPIO # to install "pip3 install --upgrade RPi.GPIO"
import sys
import os
import time
import yaml
import logging
import subprocess
import telegram       # to install "pip3 install python-telegram-bot"
GPIO.setmode(GPIO.BOARD)

##############################################################################################################################################

#token that can be generated talking with @BotFather on telegram
token = ""
bot = telegram.Bot(token=token)

"""
Send a mensage to a telegram user specified on chatId
chat_id must be a number! 
use @userinfobot to obtain yout userID from a private conversation
"""
chat_id=""

##############################################################################################################################################

# Change working dir to the same dir as this script
os.chdir(sys.path[0])

class DataCollector:
    def __init__(self, inputspins_yaml):
        self.inputspins_yaml = inputspins_yaml
        self.max_iterations = None  # run indefinitely by default
        self.inputspins = None
        self.inputspins_map_last_change = -1
        gpioinputs = self.get_inputs()
        GPIO.setwarnings(False)
#        GPIO.setup(gpioinputs, GPIO.IN)
        log.info('Configure GPIO:')
        for gpio in gpioinputs:
            log.info('\t {} - PIN {}'.format( gpio['name'], gpio['pin']))
            GPIO.setup(gpio['pin'], GPIO.IN)

    def get_inputs(self):
        assert path.exists(self.inputspins_yaml), 'Inputs not found: %s' % self.inputspins_yaml
        if path.getmtime(self.inputspins_yaml) != self.inputspins_map_last_change:
            try:
                log.info('Reloading inputs as file changed')
                new_map = yaml.load(open(self.inputspins_yaml), Loader=yaml.FullLoader)
                self.inputspins  = new_map['inputs']
                self.inputspins_map_last_change = path.getmtime(self.inputspins_yaml)
            except Exception as e:
                log.warning('Failed to re-load inputs, going on with the old one.')
                log.warning(e)
        return self.inputspins

    def collect_and_store(self):
        inputs = self.get_inputs()

        datas = dict()
        list = 0
        for parameter in inputs:
            list = list + 1
            if parameter['normally'] == 0 :
                datas[parameter['name']] = True
            else :
                datas[parameter['name']] = False

		## inicio while :
        while True:
            list = 0
            for parameter in inputs:
                list = list + 1
                try:
                    statusInput =  not GPIO.input(parameter['pin'])
                    if statusInput != datas[parameter['name']]:
                        datas[parameter['name']] = statusInput
                        log.info('{} - PIN {} - Status {}'.format( parameter['name'], parameter['pin'], int(statusInput)))
                        if statusInput == False :
                            bot.sendMessage(chat_id=chat_id, text=parameter['message0'])
                        else :
                            bot.sendMessage(chat_id=chat_id, text=parameter['message1'])
                except Exception as e:
                    log.error('Error to read input!')
                    log.error(e)
                    raise
                time.sleep(0.01)
 
			## delay 1s between read inputs
            time.sleep(1)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--inputspinsmessage', default='inputs_pins_message.yml',
                        help='YAML file containing relation inputs, name, type etc. Default "inputs_pins_message.yml"')
    parser.add_argument('--log', default='CRITICAL',
                        help='Log levels, DEBUG, INFO, WARNING, ERROR or CRITICAL')
    parser.add_argument('--logfile', default='',
                        help='Specify log file, if not specified the log is streamed to console')
    args = parser.parse_args()
    loglevel = args.log.upper()
    logfile = args.logfile

    # Setup logging
    log = logging.getLogger('input-logger')
    log.setLevel(getattr(logging, loglevel))

    if logfile:
        loghandle = logging.FileHandler(logfile, 'w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        loghandle.setFormatter(formatter)
    else:
        loghandle = logging.StreamHandler()

    log.addHandler(loghandle)

    log.info('Sleep 60 seconds for booting')

    time.sleep(60)

    log.info('Started app')

    collector = DataCollector(inputspins_yaml=args.inputspinsmessage)

    collector.collect_and_store()

    GPIO.cleanup()
