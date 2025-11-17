Camera Mascara - a single-sensor masked camera which can take single-pixel or Fourier images with strange perspectives.

This repository has developed into a "server" which can run on the a Raspberry Pi to use a Pi Hat. (Originally the code ran on a host Pc/Mac and controlled an Arduino via Firmata.) To support this there are two other repositories:
  - a Kicad design for the Pi Hat with amplifier, ADC and controls (aka Jonny Zero Hats) https://github.com/scipilot/camera-mascara-jzh
  - a Vue web app UI, (optional if you are happy to run Python over SSH) - https://github.com/scipilot/camera-mascara-vue-pocketbase


Inspired [Instructables: Non-line-of-sight Imaging With a Photoresistor and Projector ](https://www.instructables.com/Non-line-of-sight-Imaging-With-a-Photoresistor-and/)


**Phase 1 (July/August 2025):** was a "reproduction study" of the original project by Jon Bumstead of OKO Optics, in Ardiuno and Firmata (on breadboard with many changes, variations and experiments with different sensors, op amps, etc).

During this phase I built many versions of different op-amp circuits on breadboard and tried several opto products (LDR, photodiodes, phototransistors) via an Ardiuno. I learned a lot, broke a lot, and came up with a design for a phase 2 on PCB. I documented my observations in detail and have summarised the knowledge gained, pitfalls and stupid mistakes - epic blog post to come.


**Phase 2 (October 2025):** Standalone device implementation in a Pi Zero custom Hat

Phase 2 goal was to make a portable user-friendly version of the camera avoiding all the technical knowledge and removing the need for a PC to drive it. 
Also to allow the continued experiments with different sensors and amplifiers in a more stable environment. See the above Kicad project for more details.

The design uses Pocketbase as a simple server, database and API to store the images and process jobs, and serve the UI.


## Setup instructions

A) Build the Pi Hat (see other repo)

B) install this repo into the Pi (below)

C) optionally install the Vue app (see other repo)


Install this repo on the Pi

1. First install Pocketbase [see their documentation for details]([url](https://pocketbase.io/docs/going-to-production/#minimal-setup)). Just copy the executable to somewhere sensible (e.g. `/usr/local/pocketbase/`) and then use `systemd` to keep it running (below). When its running you must apply the database schema for the camera (below), and Pocketbase is ready to go.

	v1.1 of the Pi Zero W  has no prebuilt binary, but can be built on the device: [See below.]("#Pocketbase build on a Pi Zero W v1.1")
	
	Next set the admin credentials:
	
		pocketbase superuser upsert your@email.com somepassword
	
	Next create our database structure:
	
	See the JSON structure dump in `etc/pocketbase`, and import it into the GUI: http://raspberrypi.local:8090/_/#/settings/import-collections
	
	_Note: To do this you need to run pocketbase - so either do it after creating the service below, or run it temporarily from the shell via `pocketbase serve`._


2. Next install the Camera Mascara Python code and then use `systemd` to spin up a subscriber which can await the camera jobs.

	You can install the code in a few ways, e.g. git clone the code into the Pi, or SCP or RSYNC it in from a computer. 
	The examples below assume you have installed this repo's code into `/usr/local/mascara-pocketbase/`
	
	Configure the Python to authenticate with the local Pocketbase admin user. (The default URL should work.)

			cd /usr/local/mascara-pocketbase
		    cp env.dist .env
		    nano .env
				POCKETBASE_SUPERUSER_EMAIL="your@email.com"
				POCKETBASE_SUPERUSER_PASSWORD="somepassword"
				POCKETBASE_CONNECTION_URL="127.0.0.1:8090"
	
Once our code is installed on the Pi, install two systemd services from the example definition files.


3. Install Pocketbase as a service (assume in `/usr/local/pocketbase`).

		cp systemd/pocketbase.service /lib/systemd/system/
		sudo systemctl enable mascara-pocketbase.service
		sudo systemctl start mascara-pocketbase

4. Install the camera's Pocketbase subscriber as a service (assume in `/usr/local/mascara-pocketbase/`)/

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

Then you can use the API or UI at http://raspberrypi.local:8090/ (note: installing the UI website replaces the default API view)

You can use the Admin site at http://raspberrypi.local:8090/_/


## Code Architecture Notes

The Pi hat has an I2C ADC which provides the brightness levels from the sensor via the Pi's GPIO I2C pins. Therefore the lower level of the Python code has an I2C adapter class specific to the ADC (ADS1110) which converts the binary data into sensible voltage values, and handles the encoding/decoding of the configuration options (amplification, range, bias etc). The higher-level "camera" routines defer to this class to provide voltages (or brightness levels) thus abstracting the details of the hardware.

Generally the code is class based, with a dependency-injection friendly pattern, so that some elements could be swapped in the future. For instance the ADC chip might be changed and so just a new "driver" class would be needed with its I2C or SPI specifics. The relationship with Pocketbase is also via interfaces so that it can be replaced with the NPZ file-based approach as before or another database or API. It's not perfect, but some thought was put into that. There are generally three layers, the top-level entrypoint scripts are either run by a human over SSH or run by systemd to provide a lights-out service, the middle layer is the service "business logic", and the lower layer is specific adapters for the device, database, comms etc. which are injected in via a simple DI from the top layer.

There are some service classes which perform the major features: the camera image capture, image reconstruction, a light-meter and device configuration. Mask generation has been left as a script for now as its not a frequent activity, but could be done "on demand" should a user choose a new combination of resolution / pixel size / mask type which doesn't have a mask set generated and cached yet. 

[Pocketbase]([url](https://pocketbase.io/)) was chosen as a springboard as it provides a database, server, API and CRUD admin all in one lightweight executable. It runs on the Pi itself, and so no online hosting service is required, in fact the camera can operate offline (i.e. no internet but on local wifi). Other options considered were to use an SD card to access the photos enabling a true offline device, but this is hard with the Pi being an SD-card O/S. In theory the Pocketbase server could be hosted elsewhere: on the LAN/internet, but hosting it on the Pi is convenient and portable.

This repository's Python code also runs on the Pi, and contains a Pocketbase API client to talk to the server (i.e. it's not a Pocketbase extension or plugin, just a REST API client). It subscribes to Pocketbase events to receive jobs, and posts all its results back to the database (images, brightness levels, chip configuration). 

Note: you can still run the new codebase in the old style (from phase 1), i.e. running the "run" script by hand over SSH, and having it save an NPZ file, then you can run "reconstruct" to save the image to disk, then you'd have to SCP the image out. This would be done by changing the DI injections in the top scripts, ignoring the pocketbase subscriber. 

The new code bundles up all the actions into one: configure the resolution options, run the scan, gather statistics, reconstruct the image and save it to a database record along with the stats to help with experimental research. Then all this data can be consumed over the API (see UI repo).

Each Pytohn file has a PURPOSE header, for more details on the tools available (like calibration, framing the subject, light meter, mask generation etc).


## Pocketbase build on a Pi Zero W v1.1

The Pi Zero W v1.1 is ARM11 which is Armv6, but the pocketbase server only has prebuilt Armv7, which doesn't run ("Illegal instruction!" https://github.com/pocketbase/pocketbase/issues/710 )
However it can be built on the Pi and requires Go.

Install Go 

	wget https://go.dev/dl/go1.25.1.linux-armv6l.tar.gz
	rm -rf /usr/local/go && tar -C /usr/local -xzf go1.25.1.linux-armv6l.tar.gz

Build Pockebase on the Pi

	cd pocketbase-0.30.0
	nano .goreleaser.yaml 	
		- change goarm=7 to goarm=6 
	cd examples/base
	GOOS=linux GOARCH=arm CGO_ENABLED=0 go build
	./base serve

Here "base" is just the name of the executable build in the in the example. You can rename it "pocketbase".

You can then add the admin user like this:

	./base superuser upsert your@email.com somepassword
