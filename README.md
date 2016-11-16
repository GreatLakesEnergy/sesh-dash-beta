# README #

# sesh-dash-beta
SESH Dashboard beta. Working dev code.
Sesh-dashboard is a dasboard that's designed to display data from you Solar Energy system. It's built on top of python django. Data coming into the system can come form Victron QUattro inverters- Via CCGX/ Enphase micro inverters via Envoy.
It also has the capacity to get data from both systems locally through modbus-TCP(CCGX) or scraping of the envoy(web scraping)

### How do I get set up using a dev VM? ###

**Make sure you have [Vagrant](https://www.vagrantup.com/downloads.html), [Virtualbox](https://www.virtualbox.org/wiki/Downloads) and [Ansible](http://docs.ansible.com/ansible/intro_installation.html) installed.**

Follow the steps below to setup a development environment. This will setup a virtual machine with the required dependencies:
If you wish to not use a virtual-machine you can skip to virtualenvonly section.
 1. Clone this repo:
    `$ git clone https://github.com/GreatLakesEnergy/sesh-dash-beta.git`
 1. CD into the directory:
    `$ cd sesh-dash-beta`
 1. First time you run this, it will provision a machine. May take 10-15 minutes to do so:
    `$ vagrant up`
 1. SSH into the newly created VM:
    `$ vagrant ssh`
 1. CD into the working directory:
    `$ cd ~/dev/sesh/`
 1. Install python dependencies:
    `$ sudo pip install -r requirements.txt`
 1. Install bower
   ` $ sudo npm install -g bower`
 1. Get the UI components:
    `$ python ./manage.py bower_install`
 1. Collect Static files in one place:
    `$ python ./manage.py collectstatic`

#### How do I get setup with a Virtualenv only? ####
1. Make sure system level dependencies are installed first see playbook.yml
1. Create a local virtual-env (install virtualenv if you dont have it already):
    `$ virtualenv <sesh-dash-beta>`
1. Activate your virtual env
    `$cd <virtual-env-location>/bin`
    `$source activate` 
1. Install requirements defined in requirements.txt:
    `$ requirements.txt > pip install -r requirements.txt`
1. Install bower
   ` $ sudo npm install -g bower`
1. Get the UI components:
    `$ python ./manage.py bower_install`

### Before you start ###
You'll need to configure parameters for the APIs and Database. Copy to local_settings_example.ini to settings_local.ini in your repo and  put in your api keys and database settings.(contact repo owner for keys). Also setup database parameters
 1. Sync up local DB if using a local database:
    `$ python manage.py migrate`
 1. Collect Static files in one place:
    `$ python ./manage.py collectstatic`
 1. Move ui custom ui components into place:
    `$ cp -r ./seshdash/sesh-ui ./seshdash/static/`
 1. Create super user:
    `$ python manage.py createsuperuser`
 1. Run dev server:
    `$ python manage.py runserver 0.0.0.0:5000`
 1. Now start the browser and hit http://localhost:5000 or http://127.0.0.1:5000 and your application works!!!

### Getting Data ###
* The system requires data to be coming in from the API's this happens asynchronously and periodically
* Start celery with command in a different screen:
   ` $ celery --app=sesh.celery:app worker --loglevel=INFO --beat -E` 

### API docs ###
* victron: http://www.victronenergy.com/live/vrm_portal:vrm_juice_json_api_notes
* weather: https://developer.forecast.io/


### System Overview ###
* Sample diagram of PV system
*   ![sample system diagram ](https://raw.githubusercontent.com/GreatLakesEnergy/sesh-diagrams/master/sesh-system-diagram.png "sesh system diagram")

### Who do I talk to? ###

* Contact repo owner alp@gle.solar

