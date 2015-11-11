# README #

# sesh-dash-beta
SESH Dashboard beta. Working dev code.

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

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
