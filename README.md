# README #

# sesh-dash-beta
SESH Dashboard beta. Working dev code.
Sesh-dashboard is a dasboard that's designed to display data from you Solar Energy system. It's built on top of python django. Data coming into the system can come form Victron QUattro inverters- Via CCGX/ Enphase micro inverters via Envoy.

<<<<<<< HEAD
It also has the capacity to get data from both systems locally through modbus-TCP(CCGX) or scraping of the envoy(web scraping)
=======
This README would normally document whatever steps are necessary to get your application up and running.

**Make sure you have [Vagrant](https://www.vagrantup.com/downloads.html), [Virtualbox](https://www.virtualbox.org/wiki/Downloads) and [Ansible](http://docs.ansible.com/ansible/intro_installation.html) installed.**

Follow the steps below to setup a development environment. This will setup a virtual machine with the required dependencies:
 1. `git clone https://github.com/GreatLakesEnergy/sesh-dash-beta.git`
 1. `cd sesh-dash-beta`
 1. `vagrant up`
 1. `vagrant ssh`
 1. `cd ~/dev/sesh/`
 1. `sudo pip install -r requirements.txt`

To run the development server, rename the settings_local.ini.txt file to settings_local.ini and add Database settings and Secret Key
 

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)
>>>>>>> c0fae660a75c666ecccb8461686fdca6852faee0

### How do I get set up? ###

* Create a local virtual-env (install virtualenv if you dont have it already)
    `$ virtualenv <sesh-dash-beta>`
* Install requirements defined in
    `$ requirements.txt > pip install -r requirements.txt`
* Get the UI components with
   ` $ bower ./manage.py bower install`
* You'll need to configure paramters for the APIs. Modify  settings_local.ini to put in your api keys and databse settings.(contact repo owner for keys)

### Getting Data ###
* The system requires data to be coming in from the API's this happens asynchronously and periodically
* Start celery with command in a different screen
   ` $ celery --app=sesh.celery:app worker --loglevel-INFO --beat`

### API docs ###
* enphase: https://developer.enphase.com/
* victron: http://www.victronenergy.com/live/vrm_portal:vrm_juice_json_api_notes
* weather: https://developer.forecast.io/


### System Overview ###
* Sample diagram of PV system
*   ![sample system diagram ](https://raw.githubusercontent.com/GreatLakesEnergy/sesh-diagrams/master/sesh-system-diagram.png "sesh system diagram")

### Who do I talk to? ###

* Contact repo owner alp@gle.solar

