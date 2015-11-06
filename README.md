# README #

# sesh-dash-beta
SESH Dashboard beta. Working dev code.
Sesh-dashboard is a dasboard that's designed to display data from you Solar Energy system. It's built on top of python django. Data coming into the system can come form Victron QUattro inverters- Via CCGX/ Enphase micro inverters via Envoy.

It also has the capacity to get data from both systems locally through modbus-TCP(CCGX) or scraping of the envoy(web scraping)

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Create alocal virtual-env
* Install requirement defined in requirements.txt
* You'll need to configure paramters for the APIs. Modify  settings_local.ini to put in your api keys and databse settings.
* Start cellary with this command to start getting data  form your sources.  celery --app=sesh.celery:app worker --loglevel-INFO


### System Overview ###
* 

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
