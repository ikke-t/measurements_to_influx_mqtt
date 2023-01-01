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
