import bluetooth
import pymongo
import sys
import pika
import time
import re
from rmq_params import *

# Incorrect arguments handlings
if len(sys.argv) != 3:
    sys.stderr.write("Please run bridge with correct number of arguments")
    sys.exit(0)

if sys.argv[1] != "-s":
    sys.stderr.write("Wrong argument specified")
    sys.exit(0)

# Readable variables : m_queues is a set
m_username = rmq_params['username']
m_password = rmq_params['password']
m_host = 'localhost'
m_virtual_host = rmq_params['vhost']
m_exchange = rmq_params['exchange']
m_queues = rmq_params['queues']
m_master_queue = rmq_params['master_queue']
m_status_queue = rmq_params['status_queue']
m_repository_host = sys.argv[2]  # The ip address

# Init MongoDB using default params: Checkpoint 01
# Drop all related queues inside imported queues to database
database = pymongo.MongoClient()[m_exchange]

for m_queue in list(m_queues):
    database[m_queue].drop()

print(
    "[Checkpoint 01] Connected to database %r on MongoDB server at %r" %
    (m_exchange, m_host)
)

# Checkpoint 02
# Set up a connection to the RabbitMQ server on the repository with the
# imported variables and ip address host, port is already set DEFAULT
m_credentials = pika.PlainCredentials(
    m_username,
    m_password
)

parameters = pika.ConnectionParameters(
    host=m_repository_host,
    virtual_host=m_virtual_host,
    credentials=m_credentials
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

print(
    "[Checkpoint 02] Connected to vhost %r on RMQ Server at %r as user %r" %
    (m_host, m_repository_host, m_username)
)

# Bluetooth connection : Checkpoint 03 to 04
# Magic happens that Connie performed

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
nearby_devices = bluetooth.discover_devices()

# Bind at port 1 and listen
server_socket.bind(("", 1))
server_socket.listen(1)

print("[Checkpoint 03] Created RFCOMM Bluetooth socket on port 1")


# Variables for LED status colors
connected_led_color = "green"
disconnected_led_color = "red"
publish_led_color = "purple"
consume_led_color = "yellow"
history_led_color = "blue"

# Printing and publish function for status_queue and LED color


def publish_to_status_queue_led(led_color):
    channel.basic_publish(
        exchange=m_exchange,
        routing_key=m_status_queue,
        body=led_color
    )
    print(
        "[Checkpoint p-01] Published message with routing_key: %r" %
        m_status_queue
        )

    print("[Checkpoint p-02] Message: %s" % led_color)

# Declare our exchange
channel.exchange_declare(exchange=m_exchange, exchange_type='direct')

# Outer hile loop to prevent Bluetooth disconnect's crash
# and instead have the program listens for new Bluetooth connections
while True:
    # Get the Bluetooth socket information for printing to console
    client_socket, address = server_socket.accept()

    print(
        "[Checkpoint 04] Accepted RFCOMM Bluetooth connection from %r" %
        str(address)
    )

    # Publish to status queue with LED green (start up connection)
    # to repository
    publish_to_status_queue_led(connected_led_color)

    # Checkpoints 05

    print("[Checkpoint 05] Sending Exchange and Queue names")
    
    # Print to information and queues' names to the Bluetooth device
    client_message = "Communicating on Exchange: %r \r\n" % m_exchange
    client_socket.send(client_message)
    client_message = "Available Queues: \r\n"
    client_socket.send(client_message)

    for m_queue in m_queues:
        client_message = "%r\r\n" % m_queue
        client_socket.send(client_message)
    
    # Infinite loop for bluetooth and processing
    try:
        while True:
            # Receive data from the Bluetooth device
            bluetooth_received_command = client_socket.recv(1024)
            print(
                "[Checkpoint 06] Received RFCOMM Bluetooth data: %r" %
                bluetooth_received_command
            )

            if (bluetooth_received_command.decode("utf-8") != "\r\n"):
                # Get rid of the "b'" in front
                bluetooth_received_command = bluetooth_received_command.decode(
                    "utf-8"
                )
                
                # Get rid of carriage and new line from the command data
                bluetooth_received_command.rstrip()

                # Check if the command is appropriate using the regular expression
                # for alphanumeric/punctuational messages
                # command queue must be alphanumeric
                # correct command
                bluetooth_received_command = bluetooth_received_command
                pattern = re.compile('^(p:\w+ "([#-~]|[! ])+"$)|([ch]:\w+$)|([ch]:\w+$)')
                match = pattern.match(bluetooth_received_command)

                # parses the string
                action = bluetooth_received_command[0]

                collection_array = []
                for m_queue in m_queues:
                    collection_array.append(m_queue)
                    
                collection = ""
                i = 2

                # get_collection_check is for while loop processing to get the collection name (queue)
                # check is for Collection check 
                get_collection_check = False
                check = False
                
                # Process if valid command matched
                if match is not None:
                    while(not get_collection_check):
                        collection = collection + bluetooth_received_command[i]
                        i += 1
                        if (i >= len(bluetooth_received_command)):
                            get_collection_check = True
                        elif (bluetooth_received_command[i] == " "):
                            get_collection_check = True
                    # Check if the given collection is in the imported collections (m_queues)
                    for x in collection_array:
                        if x == collection:
                            check = True

                # Proceeds if database in collection and matched
                if (check and match is not None):
                    if(action == 'p'):
                        message = ""
                        i = i + 2
                        while(bluetooth_received_command[i] != '"'):
                            message = message + bluetooth_received_command[i]
                            i = i + 1
                        # end of string parsing
                        publish_to_status_queue_led(publish_led_color)

                        # Generate dictionary as specified and store in MongoDB
                        ticks = time.time()
                        id = "team_27$" + str(ticks)

                        coll = database[collection]

                        post = {
                            "Action": action,
                            "Place": m_exchange,
                            "MsgID": id,
                            "Subject": collection,
                            "Message": message
                        }

                        channel.basic_publish(
                            exchange=m_exchange,
                            routing_key=collection,
                            body=message
                        )

                        print("[Checkpoint p-01] Published message with routing_key %r" % collection)
                        print("[Checkpoint p-02] Message: %s" % message)
                        coll.insert_one(post)

                        # Print to checkpoint post
                        print("[Checkpoint m-01] Stored document in the collection %r in MongoDB Database %r" % (collection, m_exchange))
                        print("[Checkpoint m-02] Document: " + str(post))
                        
                    elif(action == "h"):
                        publish_to_status_queue_led(history_led_color)
                        print("[Checkpoint h-01] Printing history of Collection %r in MongoDB Database %r" % (collection, m_exchange))
                        print("[Checkpoint h-02] Collection: %r" % collection)
                        
                        # Prints all of the posts in the collections
                        coll = database[collection]
                        k = 0
                        
                        for post in coll.find():
                            print("Document " + str(k) + ": " + str(post))
                            k = k + 1
                            
                    elif(action == "c"):
                        coll = database[collection]   
                        publish_to_status_queue_led(consume_led_color)

                        # Basic consume with assignment to temporary variables
                        (method, properties, body) = channel.basic_get(queue=collection)

                        # Handling for empty message
                        if method is not None:
                            print(
                                "[Checkpoint c-01] Consumed a message published with routing_key: %r" %
                                method.routing_key
                            )
                            # Send consumed message to Bluetooth client
                            print("[Checkpoint c-02] Message: %s" % body.decode("utf-8"))
                            print("[Checkpoint c-03] Sending to RFCOMM Bluetooth client.")
                            client_socket.send("%s\r\n" % body.decode("utf-8"))
                            
                            # Generate Dictionary as specified and store in MongoDB
                            ticks = time.time()
                            id = "team_27$" + str(ticks)

                            coll = database[collection]

                            post = {
                                "Action": action,
                                "Place": m_exchange,
                                "MsgID": id,
                                "Subject": collection,
                                "Message": ""
                            }

                            coll.insert_one(post)

                            # Print the checkpoint post
                            print(
                                "[Checkpoint m-01] Stored document in collection %r in MongoDB database %r" %
                                (collection, m_exchange)
                            )
                            print("[Checkpoint m-02] Document: " + str(post))
                    else:
                        client_socket.send("[Error] Invalid Action" + "\r\n")
                else:
                    # If collection check and/or the command match didn't pass
                    if not check and match:
                        client_socket.send("[Error] Queue doesn't exist \r\n")
                    else:
                        client_socket.send("[Error] Wrong command \r\n")

    except IOError:
        # Type of IOError thrown when the Bluetooth disconnects
        # Publish to status queue with red disconnect led
        print("[Checkpoint 07] RFCOMM Bluetooth client disconnected")
        publish_to_status_queue_led(disconnected_led_color)
    except BluetoothError:
        print("[Checkpoint 07] RFCOMM Bluetooth client disconnected")
        publish_to_status_queue_led(disconnected_led_color)
    except:
        # Close current connections and look for another connection from
        # beginning of the while loop
        client_socket.close()
        server_socket.close()