# README #

# sesh-dash-beta
SESH Dashboard beta. Working dev code.
Sesh-dashboard is a dasboard that's designed to display data from you Solar Energy system. It's built on top of python django. Data coming into the system can come form Victron QUattro inverters- Via CCGX/ Enphase micro inverters via Envoy.

It also has the capacity to get data from both systems locally through modbus-TCP(CCGX) or scraping of the envoy(web scraping)

### How do I get set up? ###

* Create alocal virtual-env
* Install requirement defined in requirements.txt
* You'll need to configure paramters for the APIs. Modify  settings_local.ini to put in your api keys and databse settings.
* Start cellary with this command to start getting data  form your sources.  celery --app=sesh.celery:app worker --loglevel-INFO

### API locations ###
* enphase: https://developer.enphase.com/
* victron: http://www.victronenergy.com/live/vrm_portal:vrm_juice_json_api_notes
* weather: https://developer.forecast.io/


### System Overview ###
* Sample diagram of PV system
*   ![sample system diagram ](https://raw.githubusercontent.com/GreatLakesEnergy/sesh-diagrams/master/sesh-system-diagram.png "sesh system diagram")

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
