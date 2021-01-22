#!/bin/bash
# flask settings
export FLASK_APP=~/GLAMORISE/web_interface/web_api.py
export FLASK_DEBUG=0

nohup flask run --host=0.0.0.0 --port=5000 > ~/GLAMORISE/log.txt 2>&1 &
