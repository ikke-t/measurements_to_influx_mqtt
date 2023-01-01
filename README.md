# Measurements to influxdb and mqtt

This little script reads bluewalker output from socket. Bluewalker
dumps Ruuvi and Xiaomi Mijia bluetooth tag info to socket as JSON.

Define mqtt and influxdb parameters to ini file before starting this.

There is [example ini file](measurements_to_influx_mqtt-example.ini).
Fill in the values, and remove -example from the name.

There is also
[systemd service file](measurements_to_influx_mqtt.service) to help
running this as user right after boot.

Copy the service file to e.g. ```/home/pi/.config/systemd/user/```
and do run
```
systemctl --user daemon-reload
systemctl --user enable --now measurements_to_influx_mqtt.service
sudo loginctl enable-linger pi
```

Then you need to make sure bluewalker is running, see guide here
[for telegraf](https://gitlab.com/jtaimisto/bluewalker/-/issues/5)
, just drop the telegraf pieces.

# Add MQTT devices to Home-Assisstant

Here is example what I added to my mqtt.yaml:

```
sensor:

  - name: Alakerran lämpötila
    unique_id: 'a4:c1:38:aa:bb:cc_t'
    state_topic: 'sensors/a4:c1:38:aa:bb:cc'
    value_template: '{{ value_json.temperature }}'
    device_class: temperature
    unit_of_measurement: °C
    device:
      suggested_area: Olohuone
      identifiers: 'a4:c1:38:aa:bb:cc'
      name: Mijia Olohuone
      manufacturer: Xiaomi
      model: Mijia LYWSD03MMC
      configuration_url: https://pvvx.github.io/ATC_MiThermometer/TelinkMiFlasher.html
    
  - name: Alakerran kosteus
    unique_id: 'a4:c1:38:fa:e3:46_h'
    state_topic: 'sensors/a4:c1:38:aa:bb:cc'
    value_template: '{{ value_json.humidity }}'
    device_class: humidity
    unit_of_measurement: '%'
    device:
      suggested_area: Olohuone
      identifiers: 'a4:c1:38:aa:bb:cc'

  - name: Alakerran Xiaomi patteri
    unique_id: 'a4:c1:38:fa:e3:46_v'
    state_topic: 'sensors/a4:c1:38:aa:bb:cc'
    value_template: '{{ value_json.level }}'
    device_class: battery
    unit_of_measurement: '%'
    device:
      suggested_area: Olohuone

  - name: Saunan lämpötila
    unique_id: 'saunaruuvi_t'
    state_topic: 'sensors/d5:d2:87:aa:bb:cc'
    value_template: '{{ value_json.temperature }}'
    device_class: temperature
    unit_of_measurement: °C
    device:
      suggested_area: Sauna
      identifiers: 'd5:d2:87:aa:bb:cc'
      name: Saunan Ruuvi
      manufacturer: Ruuvi
      model: ruuvitag

  - name: Saunan kosteus
    unique_id: 'saunaruuvi_h'
    state_topic: 'sensors/d5:d2:87:aa:bb:cc'
    value_template: '{{ value_json.humidity }}'
    device_class: humidity
    unit_of_measurement: '%'
    device:
      suggested_area: Sauna
      identifiers: 'd5:d2:87:aa:bb:cc'

  - name: Saunan Ruuvi patteri
    unique_id: 'saunaruuvi_v'
    state_topic: 'sensors/d5:d2:87:aa:bb:cc'
    value_template: '{{ value_json.voltage }}'
    device_class: voltage
    unit_of_measurement: V
    device:
      suggested_area: Sauna
```
