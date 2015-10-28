# Android Events Catalog

## Introduction
This project is an example of an Item Catalog for Project 3 for the Udacity FSND.
. It lists cities and events in each city. This project is developed for Python 2.7.

## Requirements
Flask == 0.9<br>
SQLAlchemy == 1.0.7<br>
SeaSurf == 0.1.21<br>
For easy installation, run pip istall -r requirements.txt. Note, you may need to run as root using sudo.

## Set-up
The data is stored in a sqlite database. To create the database, run: python database_setup.py  To load the database, run: python lotsofevents-users.py  

## Usage
The website can be viewed at: localhost:8000 after running python project.py. New events can be added, edited, and deleted by logged in users. Data is also accessible via a JSON [1] and XML [2] endpoint.
<br>
[1] http://localhost:8000/all-events/JSON
<br>
[2] http://localhost:8000/all-events/XML
