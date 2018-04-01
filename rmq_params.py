#!/usr/bin/env python3
rmq_params = {
    "vhost": "ex_vhost",
    "username": "ex_user",
    "password": "ex_password",
    "exchange": "squires",
    "queues": {"messages", "events", "food"},
    "master_queue": "ex_master",
    "status_queue": "ex_status"
}
