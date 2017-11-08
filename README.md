# NetApps - Assignment 2 - Wishing Well
# Team 27
## Hung Nguyen and Connie Lim
* dnhung7@vt.edu
* conniel1@vt.edu

### System Syntax
* The Bridge Pi takes the IP address of the Repository Pi as an input parameter for its program interface. Then, the user will have to wait
until checkpoint 3 pops up on the terminal to connect via Serial Bluetooth Terminal app and start inputting commands. The message queue operations let users put in messages in the repository for anyone to consume and read from, which is the intent of modeling a wishing well (but better?)
* Errors will be outputted for invalid commands of the bluetooth

### How to run
* Make sure the Repository Pi's RabbitMQ server is configured such that the vhost specified in rmq_params has all permissions for the user specified in rmq_params (rabbitmqctl add_user, add_vhost, and set_permission)
* Run the following commands on the Bridge Pi to start the MongoDB server: sudo mongod --dbpath /var/lib/mongodb/ --journal
* Run this in another terminal of the Bride Pi: mongo
* Run the repository on the Repository Pi with only with: python3 repository.py  ( make sure rmq_params.py exist in the directory of the file )
* Run the bridge file in a separate terminal on the Bridge Pi with only : python3 bridge <REPOSITORY_IP_ADDRESS> ( also make sure rmq_params.py exist as well)
* Make sure the Bluetooth Device and the Bridge Pi are connected through Bluetooth
* Wait until Checkpoint 3 of the bridge to connect the serial interface on the Bluetooth Device
* Start inputting commands on the interface of the Bluetooth Device

### Libraries used:
* pika : rabbitMQ documentation and tutorials
* time
* sys
* bluetooth : pybluez tutorials for the servers
* pymongo : mongoDB documentation
* re : regular expression online tool at https://regexr.com/

### Description of team member contribution:
* Hung worked on the repository and some of the bridge. He got the RabbitMQ to work and outputted the LED statusses and consume message and collection, and all of the produce/consumes on both the bridge and the repository.
* Connie worked on the bridge.  She got the MongoDB, Bluetooth connection, and the parsing to work. She also did all the sending and receiving to MongoDB.  
* Both worked together on error handlings when parsing and debugging .