#!python3
"""
This module sends bluewalker ruuvi or mijia mesurement values
into influxdb. It is recommended to run this from systemd.

To get going with influxdb:
    python3 -m venv .
    source bin/activate
    pip install influxdb-client paho-mqtt
https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/

Author: Ilkka Tengvall <ilkka.tengvall@iki.fi>
License: GPLv3 or later
"""

import time
from datetime import datetime
import json
import socket
import configparser
import logging
import os, os.path
import sys
import signal
import paho.mqtt.client as mqtt
from paho.mqtt import publish
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def get_config():
    config = configparser.ConfigParser()
    config.read('measurements_to_influx_mqtt.ini')

    conf['verbosity'] = config.get('debug', 'verbosity', fallback='NOTSET')
    conf['socket_path'] = config.get('global', 'socket_path') 
    conf['mqtt_broker'] = config.get('mqtt', 'mqtt_broker')
    conf['mqtt_topic'] = config.get('mqtt', 'mqtt_topic')
    conf['influx_url'] = config.get('influx2', 'url')
    conf['influx_token'] = config.get('influx2', 'token')
    conf['influx_bucket'] = config.get('influx2', 'bucket')
    conf['influx_org'] = config.get('influx2', 'org')

    return conf

def signal_handler(signal, frame):
    print('\nterminating gracefully.')
    client.disconnect()
    server.close()
    os.remove(conf['socket_path'])
    sys.exit(0)

# The callback for when the client receives a CONNACK response from the MQTT server.
# pylint: disable=unused-argument,redefined-outer-name
def on_connect(client, userdata, flags, rc):
    logging.info('Connected to MQTT broker with result code %s', str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('$SYS/#')

def send_measurements_to_mqtt(m, conf):
    """
    Send the given data to mqtt
    """
    data = {}
    data['type'] = m['type']
    data['address'] = m['device']['address']
    data['humidity'] = round(m['sensors']['humidity'], 1)
    data['temperature'] = round(m['sensors']['temperature'], 1)

    if (m['type'] == "ruuvi"):
        data['voltage'] = round(m['sensors']['voltage']/1000, 2)
        data['pressure'] = m['sensors']['pressure']
        data['accelerationX'] = m['sensors']['accelerationX']
        data['accelerationY'] = m['sensors']['accelerationY']
        data['accelerationZ'] = m['sensors']['accelerationZ']
        data['movementCount'] = m['sensors']['movementCount']
    if (m['type'] == 'mijia'):
        data['voltage'] = round(m['sensors']['voltage'], 2)

    logging.debug("MQTT out: %s:%s:%s",
                  conf['mqtt_topic'],
                  conf['mqtt_broker'],
                  json.dumps(data))
    publish.single(conf['mqtt_topic'], json.dumps(data), hostname=conf['mqtt_broker'])

def send_measurements_to_influxdb(m, conf):
    """
    Send data to influxdb.
    """
    time = datetime.utcnow()
    success = 0
    if (m['type'] == "ruuvi"):
        point = Point("sensor") \
            .tag('address', m['device']['address']) \
            .tag('type', m['type']) \
            .field('humidity', m['sensors']['humidity']) \
            .field('temperature', m['sensors']['temperature']) \
            .field('voltage', round(m['sensors']['voltage']/1000, 2)) \
            .field('pressure', m['sensors']['pressure']) \
            .field('accelerationX', m['sensors']['accelerationX']) \
            .field('accelerationY', m['sensors']['accelerationY']) \
            .field('accelerationZ', m['sensors']['accelerationZ']) \
            .field('movementCount', m['sensors']['movementCount']) \
            .time(time)
    if (m['type'] == 'mijia'):
        point = Point("sensor") \
            .tag('address', m['device']['address']) \
            .tag('type', m['type']) \
            .field('humidity', m['sensors']['humidity']) \
            .field('temperature', m['sensors']['temperature']) \
            .field('voltage', round(m['sensors']['voltage'], 2)) \
            .time(time)

    logging.debug(f"Writing influx: {point.to_line_protocol()}")
    client_response = conf['write_api'].write(
                          bucket=conf['influx_bucket'],
                          record=point)
    # write() returns None on success
    return client_response

if __name__ == "__main__":

	# pylint: disable=C0103
    error = False
    i = 0
    conf = {}

    signal.signal(signal.SIGINT, signal_handler)
    conf = get_config()
    logging.basicConfig(level=conf['verbosity'], format='%(levelname)s:%(message)s')
    logging.debug('loglevel %s', conf['verbosity'])

    # Get MQTT connection
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(conf['mqtt_broker'], 1883, 60)
    client.loop_start()

    # Get influxdb connection
    influxdb_client = InfluxDBClient(url=conf['influx_url'],
                                     token=conf['influx_token'],
                                     org=conf['influx_org'])
    conf['write_api']  = influxdb_client.write_api(write_options=SYNCHRONOUS)

    if os.path.exists(conf['socket_path']):
        os.remove(conf['socket_path'])

    os.umask(0o000)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(conf['socket_path'])
    server.listen(1)
    conn, addr = server.accept()

    while True:
        i += 1 
        line_in = conn.recv(1024)
        if line_in:
            data = json.loads(line_in) 
            # logging.debug(data_json)
            send_measurements_to_mqtt(data, conf)
            send_measurements_to_influxdb(data, conf)
        else:
            logging.debug("no data [%i]", i)
            time.sleep(30)

    server.close()
    os.remove(conf['socket_path'])
    client.disconnect()
    exit()

