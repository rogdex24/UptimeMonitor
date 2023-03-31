from utils.util import get_duration, localize_date_time
from utils.constants import CURRENT_TIME, LAST_DAY
from datetime import datetime, timedelta
from typing import Tuple


def uptime_last_day(data: dict, store_report: dict, curr_time: datetime, status: str) -> None:
    if status == 'inactive':
        duration = get_duration(
            data['day']['last_timestamp'], curr_time)
        store_report['uptime_last_day'] -= duration

    data['day']['last_timestamp'] = curr_time
    data['day']['last_status'] = status


def next_day(start_time_utc: datetime, end_time_utc: datetime, store_info: dict) -> Tuple[datetime, datetime]:
    cur_day = start_time_utc.weekday()
    cur_day = (cur_day + 1) % 7
    start_date = start_time_utc + timedelta(days=1)
    if cur_day in store_info:
        start_time_utc, end_time_utc = localize_date_time(
            start_date, store_info[cur_day])

    return start_time_utc, end_time_utc


def calc_overlap(start_time_utc: datetime, end_time_utc: datetime, data: dict, store_info: dict) -> timedelta:
    duration = timedelta(hours=0)

    while (start_time_utc < CURRENT_TIME):
        start = max(start_time_utc, LAST_DAY)
        end = min(end_time_utc, CURRENT_TIME)
        duration += get_duration(start, end)
        data['day']['start_time'].append(start)
        data['day']['end_time'].append(end)
        start_time_utc, end_time_utc = next_day(
            start_time_utc, end_time_utc, store_info)

    return duration


def day_check_info(store_info: dict, data: dict, store_report: dict) -> None:
    cur_day = LAST_DAY.weekday()

    if cur_day in store_info:
        start_time = store_info[cur_day]['start_time_utc'].time()
        end_time = store_info[cur_day]['end_time_utc'].time()
        
        if end_time <= start_time:  # different days
            start_time_utc, end_time_utc = localize_date_time(
                LAST_DAY, store_info[cur_day])
        else:  # same day
            if end_time < LAST_DAY.time():
                cur_day = (cur_day + 1) % 7
                start_time = store_info[cur_day]['start_time_utc'].time()
                end_time = store_info[cur_day]['end_time_utc'].time()
                if end_time <= start_time:
                    start_time_utc, end_time_utc = localize_date_time(
                        LAST_DAY, store_info[cur_day])
                else:
                    start_time_utc, end_time_utc = localize_date_time(
                        CURRENT_TIME, store_info[cur_day])
            else:
                start_time_utc, end_time_utc = localize_date_time(
                    LAST_DAY, store_info[cur_day])

        data['day']['last_timestamp'] = max(start_time_utc, LAST_DAY)
        duration = calc_overlap(start_time_utc, end_time_utc, data, store_info)

        data['day']['total_time'] = duration
        store_report['uptime_last_day'] = data['day']['total_time']


def check_out_of_bound(timestamp_utc: datetime, data: dict, store_report: dict) -> None:
    if data['day']['end_time']:
        idx = data['day']['idx']
        end_time = data['day']['end_time'][idx]
        # If the time is in the other day's business hours
        if timestamp_utc > end_time:
            # move to the next day's (start,end)
            data['day']['idx'] += 1
            # Make the remaining day hours "inactive" or "active" based on last_status
            uptime_last_day(data, store_report, end_time,
                            data['day']['last_status'])
            data['day']['last_timestamp'] = data['day']['start_time'][data['day']['idx']]


def day_post_check(data: dict, store_report: dict) -> None:

    end_time = data['day']['end_time'][-1] if data['day']['end_time'] else LAST_DAY
    check_out_of_bound(end_time, data, store_report)
    uptime_last_day(data, store_report, end_time,
                    data['day']['last_status'])

    store_report['downtime_last_day'] = data['day']['total_time'] - \
        store_report['uptime_last_day']

    for key in ['uptime_last_day', 'downtime_last_day']:
        if isinstance(store_report[key], timedelta):
            store_report[key] = round(
                store_report[key].total_seconds() / 3600, 2)
