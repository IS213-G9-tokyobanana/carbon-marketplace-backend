#!/bin/sh
service cron start
python3 checkAmqp.py
