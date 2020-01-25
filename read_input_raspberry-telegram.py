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
GPIO.setmode(GPIO.BOARD)

# Change working dir to the same dir as this script
os.chdir(sys.path[0])

class DataCollector:
    def __init__(self, influx_yaml, inputspins_yaml):
        self.influx_yaml = influx_yaml
        self.influx_map = None
        self.influx_map_last_change = -1
        log.info('InfluxDB:')
        for influx_config in sorted(self.get_influxdb(), key=lambda x:sorted(x.keys())):
            log.info('\t {} <--> {}'.format(influx_config['host'], influx_config['name']))
        self.inputspins_yaml = inputspins_yaml
        self.max_iterations = None  # run indefinitely by default
        self.inputspins = None
        self.inputspins_map_last_change = -1
        gpioinputs = self.get_inputs()
        GPIO.setwarnings(False)
#        GPIO.setup(gpioinputs, GPIO.IN)
        log.info('Configure GPIO:')
        for gpio in gpioinputs:
            log.info('\t {} - PIN {}'.format( gpio, gpioinputs[gpio]))
            GPIO.setup(gpioinputs[gpio], GPIO.IN)

    def get_inputs(self):
        assert path.exists(self.inputspins_yaml), 'Inputs not found: %s' % self.inputspins_yaml
        if path.getmtime(self.inputspins_yaml) != self.inputspins_map_last_change:
            try:
                log.info('Reloading inputs as file changed')
                self.inputspins = yaml.load(open(self.inputspins_yaml), Loader=yaml.FullLoader)
#                self.meter_map = new_map['inputs']
                self.inputspins_map_last_change = path.getmtime(self.inputspins_yaml)
            except Exception as e:
                log.warning('Failed to re-load inputs, going on with the old one.')
                log.warning(e)
        return self.inputspins

    def get_influxdb(self):
        assert path.exists(self.influx_yaml), 'InfluxDB map not found: %s' % self.influx_yaml
        if path.getmtime(self.influx_yaml) != self.influx_map_last_change:
            try:
                log.info('Reloading influxDB map as file changed')
                new_map = yaml.load(open(self.influx_yaml), Loader=yaml.FullLoader)
                self.influx_map = new_map['influxdb']
                self.influx_map_last_change = path.getmtime(self.influx_yaml)
            except Exception as e:
                log.warning('Failed to re-load influxDB map, going on with the old one.')
                log.warning(e)
        return self.influx_map

    def collect_and_store(self):
        inputs = self.get_inputs()
        influxdb = self.get_influxdb()
        t_utc = datetime.utcnow()
        t_str = t_utc.isoformat() + 'Z'

        send = False
        datas = dict()
        list = 0
        for parameter in inputs:
            list = list + 1
            datas[parameter] = False

        start_time = time.time()

		## inicio while :
        while True:
            list = 0
            for parameter in inputs:
                list = list + 1
                statusInput =  not GPIO.input(inputs[parameter])
                if statusInput != datas[parameter]:
                    datas[parameter] = statusInput
                    log.info('{} - PIN {} - Status {}'.format( parameter, inputs[parameter], int(statusInput)))
                    send = True

            if send:
                send = False
                t_utc = datetime.utcnow()
                t_str = t_utc.isoformat() + 'Z'
                json_body = [
                    {
                        'measurement': 'LocalInputsLog',
                        'tags': {
                            'id': inputs_id,
                        },
                        'time': t_str,
                        'fields': {
                            'status': int(datas[inputs_id]),
                        }
                    }
                    for inputs_id in datas
                ]
                if len(json_body) > 0:
                    influx_id_name = dict() # mapping host to name

#                    log.debug(json_body)

                    for influx_config in influxdb:
                        influx_id_name[influx_config['host']] = influx_config['name']

                        DBclient = InfluxDBClient(influx_config['host'],
                                                influx_config['port'],
                                                influx_config['user'],
                                                influx_config['password'],
                                                influx_config['dbname'])
                        try:
                            DBclient.write_points(json_body)
                            log.info(t_str + ' Data written for %d inputs in {}.' .format(influx_config['name']) % len(json_body) )
                        except Exception as e:
                            log.error('Data not written! in {}' .format(influx_config['name']))
                            log.error(e)
                            raise
                else:
                    log.warning(t_str, 'No data sent.')

                start_time = time.time()

			## delay 200 ms between read inputs
            time.sleep(0.2)


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--inputspinsmessage', default='inputs_pins_message.yml',
                        help='YAML file containing relation inputs, name, type etc. Default "inputs_pins_message.yml"')
    parser.add_argument('--influxdb', default='telegram_config.yml',
                        help='YAML file containing Influx Host, port, user etc. Default "telegram_config.yml"')
    parser.add_argument('--log', default='CRITICAL',
                        help='Log levels, DEBUG, INFO, WARNING, ERROR or CRITICAL')
    parser.add_argument('--logfile', default='',
                        help='Specify log file, if not specified the log is streamed to console')
    args = parser.parse_args()
    interval = int(args.interval)
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

    log.info('Sleep {} seconds for booting' .format( interval ))

    time.sleep( interval )

    log.info('Started app')

    collector = DataCollector(influx_yaml=args.influxdb,
                              inputspins_yaml=args.inputspinsmessage)

    collector.collect_and_store()

    GPIO.cleanup()
