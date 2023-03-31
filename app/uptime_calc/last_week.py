from utils.util import get_duration, localize_date_time
from utils.constants import CURRENT_TIME, LAST_WEEK
from datetime import datetime, timedelta, timezone
from typing import Tuple


def uptime_last_week(data: dict, store_report: dict, curr_time: datetime, status: str) -> None:
    if status == 'inactive':
        if curr_time < data['week']['last_timestamp']:
            return
        duration = get_duration(
            data['week']['last_timestamp'], curr_time)
        store_report['uptime_last_week'] -= duration

    data['week']['last_timestamp'] = curr_time
    data['week']['last_status'] = status


def week_check_info(store_info: dict, data: dict, store_report: dict) -> None:
    cur_day = LAST_WEEK.weekday()

    if cur_day in store_info:
        start_time = store_info[cur_day]['start_time_utc'].time()
        end_time = store_info[cur_day]['end_time_utc'].time()

        if end_time <= start_time:
            start_time_utc, end_time_utc = localize_date_time(
                LAST_WEEK, store_info[cur_day])
        elif end_time < LAST_WEEK.time():
            date = LAST_WEEK + timedelta(days=1)
            start_time_utc, end_time_utc = localize_date_time(
                date, store_info[(cur_day + 1) % 7])
        else:
            start_time_utc, end_time_utc = localize_date_time(
                LAST_WEEK, store_info[cur_day])

        data['week']['last_timestamp'] = max(start_time_utc, LAST_WEEK)
        duration = calc_overlap(start_time_utc, end_time_utc, data, store_info)
        data['week']['total_time'] = duration
        store_report['uptime_last_week'] = data['week']['total_time']


def next_day(start_time_utc: datetime, end_time_utc: datetime, store_info: dict) -> Tuple[datetime, datetime]:
    # change start_time_utc to the relevant 'day' basically the same but inside loop
    cur_day = start_time_utc.weekday()
    cur_day = (cur_day + 1) % 7
    start_date = start_time_utc + timedelta(days=1)
    # get time
    if cur_day in store_info:
        # localize start, end times with the date
        start_time_utc, end_time_utc = localize_date_time(
            start_date, store_info[cur_day])

    return start_time_utc, end_time_utc


def calc_overlap(start_time_utc: datetime, end_time_utc: datetime, data: dict, store_info: dict) -> timedelta:
    duration = timedelta(hours=0)
    if end_time_utc == CURRENT_TIME:
        return timedelta(days=7)

    while (start_time_utc < CURRENT_TIME):
        start = max(start_time_utc, LAST_WEEK)
        end = min(end_time_utc, CURRENT_TIME)
        duration += get_duration(start, end)
        add_to_data(data, start, end)
        start_time_utc, end_time_utc = next_day(
            start_time_utc, end_time_utc, store_info)

    return duration


def add_to_data(data: dict, start: datetime, end: datetime) -> None:
    data['week']['start_time'].append(start)
    data['week']['end_time'].append(end)


def check_out_of_bound(timestamp_utc: datetime, data: dict, store_report: dict) -> None:
    if data['week']['end_time']:
        # If the time is in the other day's business hours
        while timestamp_utc > data['week']['end_time'][data['week']['idx']]:
            end_time = data['week']['end_time'][data['week']['idx']]
            data['week']['idx'] += 1
            uptime_last_week(data, store_report, end_time,
                                data['week']['last_status'])
            # go to next day
            data['week']['last_timestamp'] = data['week']['start_time'][data['week']['idx']]

def week_post_check(data: dict, store_report: dict) -> None:

    end_time = data['week']['end_time'][-1] if data['week']['end_time'] else CURRENT_TIME
    check_out_of_bound(end_time, data, store_report)
    uptime_last_week(data, store_report, end_time, data['week']['last_status'])

    store_report['downtime_last_week'] = data['week']['total_time'] - \
        store_report['uptime_last_week']

    for key in ['uptime_last_week', 'downtime_last_week']:
        if isinstance(store_report[key], timedelta):
            store_report[key] = round(
                store_report[key].total_seconds() / 3600, 2)
