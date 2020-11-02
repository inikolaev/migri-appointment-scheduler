from datetime import datetime
from find_times import find_times
from models import ReservationType
from typing import List

import os
import typer


def format_datetime(date: datetime) -> str:
    return date.strftime('%b %d %Y %H:%M')


def display_notification(title: str, body: str):
    command = f'''osascript -e 'display notification "{body}" with title "{title}"' '''
    os.system(command)


def main(
    office: str = typer.Option(..., help='Migri office'), 
    reservation_type: List[ReservationType] = typer.Option(..., help='Migri reservation type'),
    min_date: datetime = typer.Option(..., help='Earliest appoinment date'),
    max_date: datetime = typer.Option(..., help='Latest appoinment date')
) -> None:
    min_date = min_date.astimezone()
    max_date = max_date.astimezone()

    available_slots = find_times(office, reservation_type)

    matching_slots = [
        (week, slot)
        for week, slot in available_slots
        if slot >= min_date and slot < max_date
    ]

    if matching_slots:
        earliest_availability = matching_slots[0][1]
        display_notification(
            'Found available time slots at Migri', 
            f'The first available time slot is on {format_datetime(earliest_availability)}'
        )


typer.run(main)