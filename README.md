# Tools for connecting to devices
# Currently working for meitrack devices. Simcom devices will not be working properly.

This is a tool for two way communications with meitrack gps cell devices as well as simcom 5360 gps cell devices.

It will pull in payloads from the devices and queue them into rabbitmq. This also allows comms back to the devices.

NOTE: Although fully featured, this is just a POC and care must be taken around device security.

Tested with Meitrack devices -> T333, T366, T366G but should also work with any device using the meitrack "GPRS" protocol
