# Migri Appoinment Scheduler

It's usually quite hard to find a time slot for appointment in Migri so I created this script which monitors availability and shows a notification on Mac OS (other OSes not supported at the moment, but PRs are welcome). 

It's possible to configure some aspects of required appoinment directly in the script. For example it is possible to configure the number of people and the type of appointment for each as well as Migri office location.

# Installation

Create a new virtual environment

```bash
python -m venv ~/.local/share/virtualenvs/migri-appoinment-scheduler
. ~/.local/share/virtualenvs/migri-appoinment-scheduler/bin/activate
pip install -r requirements.txt
```

Open crontab editor

```bash
crontab -e
```

and add the following rule which checks the schedule every 10 minutes (or whatever you like)

```
*/10 * * * * ~/migri-appointment-scheduler/find-times.sh
```

Make sure to update paths to the corresponding ones on your system in `find-times.sh` and in the command above.
