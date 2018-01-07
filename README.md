# Android Events Catalog

## Introduction
This project is an example of an Item Catalog built during the Udacity FSND. It lists cities and events in each city. This project is developed using Python 2.7. It is based on the OAuth sample from Udacity https://github.com/udacity/OAuth2.0

## Requirements

- Python 2.7
- Flask
- SQLAlchemy
- SeaSurf
- httplib2
- oauth2client
- psycopg2
- requests
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

For easy installation on an existing Linux server, run `pip install -r requirements.txt`. Note, you may need to run this as root using "sudo" as `sudo pip install -r requirements.txt`.

To prepare an environment to run the app locally, install Vagrant and Virtual Box and then run `vagrant up` from the same directory as the `Vagrantfile` for this project to configure the VM and install the needed modules. After the VM has launched, run `vagrant ssh` to login to the VM and then `cd  /vagrant` to navigate to the location of the app.

## Set-up
The data is stored in a sqlite database.

To create the database, from the terminal run:
```
python database_setup.py
```

To load the database, from the terminal run:
```
python lotsofevents-users.py
```

## Run the app
To launch the application, from the terminal run:
```
python project.py
```

## Usage
The website can be viewed at: localhost:8000. New events can be added, edited, and deleted by logged in users. Data is also accessible via a JSON [1] and XML [2] endpoints.
<br>
[1] http://localhost:8000/all-events/JSON
<br>
[2] http://localhost:8000/all-events/XML

# Screenshots
Home page <br>
![Alt text](readme-images/home.png "Home page")

<br><br>

Event Details <br>
![Alt Text](readme-images/eventDetails.png "Event Details")

<br><br>

Add New Event<br>
![Alt Text](readme-images/AddNewEvent.png "Add New Event")

<br><br>

Navigation Drawer<br>
![Alt Text](readme-images/drawer.png "Navigation Drawer")
