
from datetime import datetime, timedelta, timezone
from models import ReservationType
from typing import Dict, List, Tuple

import calendar
import json
import requests


migri_offices = {
    'helsinki': '25ee3bce-aec9-41a7-b920-74dc09112dd4'
}

migri_appointment_types = {
    'permanent-residence-permit': '3e03034d-a44b-4771-b1e5-2c4a6f581b7d',
    'family-first-and-extended-residence-permit': 'a87390ae-a870-44d4-80a7-ded974f4cb06'
}


class MigriSession:
    def __init__(self) -> None:
        self.__session = requests.Session()
        self.__session_data = None

    def __get_session_id(self) -> str:
        if self.__session_data is None:
            print('Initializing new Migri session')
            self.__session.get('https://migri.vihta.com/public/migri/#/reservation')
            response = self.__session.get('https://migri.vihta.com/public/migri/api/sessions?language=en')
            if response.ok:
                self.__session_data = response.json()
            else:
                print('Failed to initialize session')

        return self.__session_data['id']


    def get_schedule(self, office: str, week: datetime, selector: List[Dict]) -> List:
        session_id = self.__get_session_id()

        if not session_id:
            return []

        headers = {
            'authority': 'migri.vihta.com',
            'accept': 'application/json, text/plain, */*',
            'vihta-session': session_id,
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
            try:
                data = response.json()
                return data['dailyTimesByOffice']
            except:
                print(response.text)
                return []
        else:
            print(f'Failed to load schedule: status code = {response.status_code}')
            return []


def current_week_start() -> datetime:
    now = datetime.now()
    week_start = now - timedelta(days = now.weekday())
    return week_start.replace(hour=0, minute=0, second=0, microsecond=0)


def parse_time(date: str) -> datetime:
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=timezone.utc).astimezone()


def find_all_times(office: str, selector: List[Dict]) -> None:
    week = current_week_start()
    last_week = week + timedelta(weeks=15)

    session = MigriSession()

    schedule = {}
    while week <= last_week:
        week_schedule = session.get_schedule(office, week, selector)
        schedule[week] = week_schedule
        week += timedelta(weeks=1)

    return schedule


def find_times(office: str, reservation_types: List[ReservationType]) -> Tuple[datetime, datetime]:
    # Configure appointment selector
    selector = [
        dict(
            firstName='first',
            lastName='last',
            values=[migri_appointment_types[reservation_type]]
        )
        for reservation_type in reservation_types
    ]

    schedule = find_all_times(migri_offices[office], selector)

    return [
        (week, parse_time(slot['startTimestamp']))
        for week, week_schedule in schedule.items()
        for day_schedule in week_schedule
        for slot in day_schedule 
    ]
