
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import calendar
import json
import os
import requests

HELSINKI = '25ee3bce-aec9-41a7-b920-74dc09112dd4'
PERMANENT_RESIDENCE_PERMIT = "3e03034d-a44b-4771-b1e5-2c4a6f581b7d"
FAMILY_FIRST_AND_EXTENDED_RESIDENCE_PERMIT = "a87390ae-a870-44d4-80a7-ded974f4cb06"


class MigriSession:
    def __init__(self) -> None:
        self.__session = requests.Session()
        self.__session_data = None

    def __get_session_id(self) -> str:
        if self.__session_data is None:
            print('Initializing new Migri session')
            self.__session.get('https://migri.vihta.com/public/migri/#/reservation')
            response = self.__session.get('https://migri.vihta.com/public/migri/api/sessions?language=en')
            self.__session_data = response.json()

        return self.__session_data['id']


    def get_schedule(self, office: str, week: datetime, selector: List[Dict]) -> List:
        headers = {
            'authority': 'migri.vihta.com',
            'accept': 'application/json, text/plain, */*',
            'vihta-session': self.__get_session_id(),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://migri.vihta.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://migri.vihta.com/public/migri/',
            'accept-language': 'ru,en;q=0.9'          
        }

        year = week.year
        calendar_week = week.isocalendar()[1]
        url = f'https://migri.vihta.com/public/migri/api/scheduling/offices/{office}/{year}/w{calendar_week}'
        print(f'Loading schedule for week {calendar_week}')
        mirgri_request = dict(serviceSelections=selector, extraServices=[])
        response = self.__session.post(url, params=dict(start_hours=0, end_hours=24), headers=headers, data=json.dumps(mirgri_request))

        if response.ok:
            data = response.json()
            return data['dailyTimesByOffice']
        else:
            print(f'Failed to load schedule: status code = {response.status_code}')
            return []


def current_week_start() -> datetime:
    now = datetime.now()
    week_start = now - timedelta(days = now.weekday())
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)


def parse_time(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=timezone.utc).astimezone()


def format_datetime(date: datetime) -> str:
    return date.strftime('%b %d %Y %H:%M')


def print_schedule(schedule: List[List]) -> None:
    for i, day in enumerate(schedule):
        if not day:
          continue

        print(calendar.day_name[i])
        for slot in day:
            date = parse_time(slot['startTimestamp'])
            print(f'  {date.hour:02d}:{date.minute:02d}')


def find_all_times(office: str, selector: List[Dict]) -> None:
    week = current_week_start()
    last_week = week + timedelta(weeks=15)

    session = MigriSession()

    schedule = {}
    while week <= last_week:
        week_schedule = session.get_schedule(HELSINKI, week, selector)
        schedule[week] = week_schedule
        week += timedelta(weeks=1)

    return schedule


def display_notification(title: str, body: str):
    command = f'''osascript -e 'display notification "{body}" with title "{title}"' '''
    os.system(command)


# Configure min and max date of the appointment
min_date = datetime(year=2020, month=11, day=15).astimezone()
max_date = datetime(year=2021, month=1, day=29).astimezone()

# Configure appointment selector
selector = [dict(
  firstName='first',
  lastName='last',
  values=[PERMANENT_RESIDENCE_PERMIT]
), dict(
  firstName='first',
  lastName='last',
  values=[PERMANENT_RESIDENCE_PERMIT]
), dict(
  firstName='first',
  lastName='last',
  values=[FAMILY_FIRST_AND_EXTENDED_RESIDENCE_PERMIT]
)]

schedule = find_all_times(HELSINKI, selector)

all_available_slots = [
    (week, parse_time(slot['startTimestamp']))
    for week, week_schedule in schedule.items()
    for day_schedule in week_schedule
    for slot in day_schedule 
]

matching_slots = [
    (week, slot)
    for week, slot in all_available_slots
    if slot >= min_date and slot < max_date
]

if matching_slots:
    print(matching_slots)
    earliest_availability = matching_slots[0][1]
    display_notification(
        'Found available time slots at Migri', 
        f'The first available time slot is on {format_datetime(earliest_availability)}'
    )