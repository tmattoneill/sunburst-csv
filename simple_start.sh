#!/bin/bash

export MAIN_DIR=$(pwd)

pyenv activate sunchart
python app/main.py

sleep 10

cd frontend
npm run serve

# on exit or CTRL-C
cd $MAIN_DIR
