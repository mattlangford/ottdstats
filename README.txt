ottdstats is a python script/app that connect to OpenTTD servers and records history and state
into a mysql database, for future reporting

-Dependencies-

libottdadmin2 (https://github.com/Xaroth/libottdadmin2)
mysql (http://dev.mysql.com/downloads/connector/python/)

Usage: python server.py

-Configuration-

First time running the app, config.json will be automatically generated. This will contain
all configuration for the app.

servers: list of OpenTTD servers to connect to
    name: unique name of openttd server
    interface: adminport (for now)
    host: host of server
    port: port admin port is configured
    password: admin password for admin port
database: connection details for mysql database
general: general configuration information
    daemon: set to False if running as script which will query all servers once and return
            set to True to continually query
    interval: seconds between queries if daemon is set to True

-Database- Auto created first time app is created. User in configuration must have create database access.

-Credits-
efess: development
luaduck: for the initial idea
