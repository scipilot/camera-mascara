Camera Mascara - a single-sensor masked camera which can take single-pixel or Fourier images with strange perspectives.

This repository has developed into a "server" which can run on the a Raspberry Pi to use a Pi Hat. (Originally the code ran on a host Pc/Mac and controlled an Arduino via Firmata.) To support this there are two other repositories:
  - a Kicad design for the Pi Hat with amplifier, ADC and controls (aka Jonny Zero Hats) https://github.com/scipilot/camera-mascara-jzh
  - a Vue web app UI, (optional if you are happy to run Python over SSH) - https://github.com/scipilot/camera-mascara-vue-pocketbase


Inspired  by [Instructables: Non-line-of-sight Imaging With a Photoresistor and Projector ](https://www.instructables.com/Non-line-of-sight-Imaging-With-a-Photoresistor-and/)


Phase 1: a reproduction study of the original project by Jon Bumstead of OKO Optics, in Ardiuno and Firmata (on breadboard with many changes, variations and experiments with different sensors, op amps, etc).

(August 2025)


Phase 2: Standalone device reimplementation in a Pi Zero custom Hat

(October 2025)

Phase 2 uses Pocketbase as a simple server, database and API to store the images and process jobs, and serve the UI.


## Architecture
The Pi hat has an I2C ADC which provides the brightness levels from the sensor to the Pi's GPIO I2C pins. Therefore the lower level of the Python code has an I2C adapter class specific to the ADC (ADS1110) which converts the binary data into sensible voltage values, and handles the encoding/decoding of the configuration options (amplification, range, bias etc). 

Generally the code is class based, with a dependency-injection friendly pattern, so that some elements could be swapped in the future. For instance the ADC chip might be changed and so just a new "driver" class would be needed with its I2C specifics. The relationship with Pocketbase is also via interfaces so that it can be replaced with a NPZ file-based approach (as before) or another database. It's not perfect, but some thought was put into that. There are generally three layers, the top-level entrypoint scripts are either run by a human over SSH or run by systemd to provide a lights-out service, the middle layer is the service "business logic", and the lower layer is specific adapters for the device, database, comms etc. which are injected in via a simple DI from the top layer.

There are some service classes which perform the major features: the camera capture, image reconstruction, a light-meter and device configuration. Mask generation has been left as a script for now as its not a frequent activity, but could be done "on demand" should a user choose a new combination of resolution/pixel size/mask type which doesn't have a mask set generated yet. 

Pocketbase was chosen as it provides a database, server, API and CRUD admin all in one lightweight executable. It runs on the Pi itself, and so no online hosting/service is required, in fact the camera operates offline (i.e. not on the internet, but on local wifi). Other options might have been using an SD card to access the photos enabling a true offline device, but this is hard with the Pi being an SD-card O/S. In theory, the Pocketbase server could be hosted anywhere, on the LAN/internet, but hosting it on the Pi is convenient and portable.

This repository's Python code also runs on the Pi, and contains a Pocketbase API client to talk to the server (i.e. it's not a Pocketbase extension or plugin, just a REST API client). It subscribes to Pocketbase events to receive jobs, and posts all its results back to the database (images, brightness levels, chip configuration). 

Note: you can still run the new codebase in the old style (from phase 1), i.e. running the "run" script by hand over SSH, and having it save an NPZ file, then you can run "reconstruct" to save the image to disk. This is done by changing the DI injections, and ignoring the pocketbase subscriber. 

The new code bundles up all the actions into one: configure the resolution options, run the scan, reconstruct the image and save it to a database record along with some statistics to help with experiments. Then all this data can be consumed over the API (see other repo).



## Setup instructions

A) Build the Pi Hat (see other repo)
B) install this repo into the Pi (below)
C) optionally install the Vue app (see other repo)

You can install the code in a few way, e.g. install git and checkout the code into the Pi, or SCP or RSYNC it in. 
The examples below assume you have installed this repo's code into `/usr/local/mascara-pocketbase/`

First you need to install Pocketbase, which is pretty simple (see their documentation for any details). It's just a matter of copying the single executable into somewhere sensible (e.g. `/usr/local/pocketbase/`) and then using `systemd` to keep it running. Once it's installed you can apply the database schema for the camera, and Pocketbase is ready to go.  Second install this repo's Python code and use `systemd` to spin up a subscriber which can await the camera jobs.

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

See the JSON structure dump in `etc/pocketbase`, and import it into the GUI:

http://raspberrypi.local:8090/_/#/settings/import-collections


Then you can use the API or UI at http://raspberrypi.local:8090/ (note: installing the UI website replaces the default API view)

You can use the Admin site at http://raspberrypi.local:8090/_/
