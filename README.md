# Tortle (Tournament Tracker)

## About

This program was made to track the progress of a tournament and provide an easy way to review previous games as well as show player statistics over the course of a tournament.

The primary motivation for this was for a LAN party that my friends and I host semi-regularly.

I was hoping to make it more general in the sense that many different games could be incorporated into the program. However, at this stage it is only designed to be used for Heroes of Newerth. A classic, almost dead game that I enjoy.

An example of the program can be found hosted here: https://tortle.adamja.net/

## Setup

To setup the the program you can run the setup.sh script.  This assumes you have some dependencies installed:
* docker
* docker compose

This will create a ```docker/``` folder within the directory which will contain/persist the database and logs for the program.

## TODO

* Add user registration
* Map tournaments to users
* Restrict routes based on logged in user
* When creating a new match (New Match), include add section to add players so that it can be done in one action.
* Add throne icon to MVP player