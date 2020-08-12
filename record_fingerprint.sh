#!/bin/bash

sudo srsue ../../SRSLTE/srsLTE-modified/srsue/ue.conf &

sleep $1

sudo pkill -INT srsue

sleep 6 # because if srsue hasn't stopped after 5s, it is forced stopped
