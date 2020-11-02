#!/bin/sh

source ~/.local/share/virtualenvs/migri-scheduler/bin/activate
python ~/migri-appointment-scheduler/main.py --office helsinki 
               --reservation-type permanent-residence-permit 
               --reservation-type permanent-residence-permit 
               --reservation-type family-first-and-extended-residence-permit 
               --min-date 2020-11-15 
               --max-date 2020-12-29
