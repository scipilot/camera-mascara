Inspired  by [Instructables: Non-line-of-sight Imaging With a Photoresistor and Projector ](https://www.instructables.com/Non-line-of-sight-Imaging-With-a-Photoresistor-and/)

Phase 1: reproduction study of the original "OKO" project in Ardiuno and Firmata (with many changes, variations and experiments with different sensors)

(completed around August 2025)

Phase 2: standalone device reimplementation in a Pi Zero custom Hat

(experimenting from October 2025)

Phase 2 uses Pocketbase as a simple server, database and API to store the images and process jobs.
Once the code is installed on the Pi, install two systemd services:

1. Install Pocketbase as a service. (assume into /usr/local/pocketbase/)
   
    cp systemd/pocketbase.service /lib/systemd/system/
    sudo systemctl enable mascara-pocketbase.service
    sudo systemctl start mascara-pocketbase

2. Install the camera's Pocketbase subscriber

    cp systemd/mascara-pocketbase.service /lib/systemd/system/
    sudo mkdir /usr/local/mascara-pocketbase/
    sudo systemctl enable mascara-pocketbase.service
    sudo systemctl start mascara-pocketbase

To view logs or diagnose
 
    sudo tail -f /usr/local/mascara-pocketbase/std.log
    journalctl -u mascara-pocketbase.service

To edit definition
    nano /lib/systemd/system/mascara-pocketbase.service
    systemctl daemon-reload


3. Install the Pockebase database structure

See the JSON structure dump in projector/etc/pocketbase, and import it into the GUI:

http://raspberrypi.local:8090/_/#/settings/import-collections

Then you can use the API at http://raspberrypi.local:8090/


