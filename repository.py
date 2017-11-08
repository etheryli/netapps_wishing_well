#!/usr/bin/env python3

import pika
import sys
from rmq_params import *

# Check for valid argument
if len(sys.argv) != 1:
    sys.stderr.write('Please run repository without any arguments')
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

# Set up a connection to the RabbitMQ server with the
# imported variables, port is already set DEFAULT
m_credentials = pika.PlainCredentials(
    m_username,
    m_password
)

parameters = pika.ConnectionParameters(
    host=m_host,
    virtual_host=m_virtual_host,
    credentials=m_credentials
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Checkpoint 01 for connection parameters
print(
    "[Checkpoint 01] Connected to vhost %r on RMQ server at %r as user %r" %
    (
        m_virtual_host,
        m_host,
        m_username
    )
)

# Declare the imported exchange and all of the imported queues
channel.exchange_declare(
    exchange=m_exchange,
    exchange_type='direct'
)

channel.queue_declare(queue=m_master_queue)
channel.queue_declare(queue=m_status_queue)

for m_queue in m_queues:
    channel.queue_declare(queue=m_queue)

# Purge all queues
channel.queue_purge(queue=m_master_queue)
channel.queue_purge(queue=m_status_queue)

for m_queue in m_queues:
    channel.queue_purge(queue=m_queue)

# Unbind and rebind all queues to exchange
channel.queue_unbind(queue=m_master_queue, exchange=m_exchange)
channel.queue_unbind(queue=m_status_queue, exchange=m_exchange)

for m_queue in m_queues:
    channel.queue_unbind(queue=m_queue, exchange=m_exchange)
    channel.queue_bind(queue=m_queue, exchange=m_exchange)

channel.queue_bind(queue=m_master_queue, exchange=m_exchange)
channel.queue_bind(queue=m_status_queue, exchange=m_exchange)

# Additional bindings between master queue and exchange with
# routing key as the queue name for all queues except master
channel.queue_bind(
    queue=m_master_queue,
    exchange=m_exchange,
    routing_key=m_status_queue
)

for m_queue in m_queues:
    channel.queue_bind(
        queue=m_master_queue,
        exchange=m_exchange,
        routing_key=m_queue
    )


# Consume messages from bridge through only the master queue
# regardless of the intended-queue published:
# - status queue routing key prints out the LED color : Checkpoint 1-01
# - all other queue routing key prints out to console : Checkpoints 03 to 04


def callback(ch, method, properties, body):
    if method.routing_key == m_status_queue:
        print(
            "[Checkpoint 1-01] Flashing LED to %s" %
            body.decode("utf-8")
        )
        return
    print(
        "[Checkpoint 03] Consumed a message published with routing key %r" %
        method.routing_key
    )
    print("[Checkpoint 04] Message: %s" % body.decode("utf-8"))


# Consumes once : Checkpoint 2
channel.basic_consume(callback, queue=m_master_queue)
print(
    "[Checkpoint 02] Consuming messages from %r queue" %
    m_master_queue
)

# Consumes indefinitely
channel.start_consuming()
