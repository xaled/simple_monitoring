#!/bin/bash
HOST="user@host"
LOG_FILE="monitoring.log"
JSON_FILE="monitoring.json"
KEY="~/.ssh/pub_rsa"
ssh -i $KEY $HOST ./monitor.py monitor.conf.json > /dev/null
ssh -i $KEY $HOST cat monitor.out >> $JSON_FILE
echo >> $JSON_FILE
ssh -i $KEY $HOST cat monitor.log >> $LOG_FILE

