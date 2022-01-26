# Tools for connecting to devices
# Currently working for meitrack devices. Simcom devices will not be working properly.

This is a tool for two way communications with meitrack gps cell devices as well as simcom 5360 gps cell devices.

It will pull in payloads from the devices and queue them into rabbitmq. This also allows comms back to the devices.

NOTE: Although fully featured, this is just a POC and care must be taken around device security.

Tested with Meitrack devices -> T333, T366, T366G but should also work with any device using the meitrack "GPRS" protocol.

The main purpose of this project is to pull in GPS data from a range of devices and push them through to a web framework for visualisation (https://github.com/scattym/python-tool-geotool). It will carry forward GPS data, Cell Data, Camera images and Taxi Fare data. Along with other ancillary data.

Overall design:

![Overall Design](https://github.com/scattym/python-tool-simchatserver/blob/master/misc/SimchatServerDesign.png?raw=true)
