# item-catalog
Project 3 for the Udacity FSND.

This project is an example of an Item Catalog. It lists cities and events in each city. The data is stored in a sqlite database. To create the database, run: python database_setup.py  To load the database, run: python lotsofevents-users.py  The website can be viewed at: localhost:8000 after running python project.py.

Data can be added and edited by logged in users. Data is also accessible via a JSON [1] and XML [2] endpoint.

[1] http://localhost:8000/all-events/JSON
[2] http://localhost:8000/all-events/XML
