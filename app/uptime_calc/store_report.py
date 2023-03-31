from config.database import store_hours, store_status, store_timezones
from utils.constants import CURRENT_TIME, LAST_HOUR, LAST_DAY, LAST_WEEK
from utils.util import local_time_to_utc, localize_date_time
from .last_hour import uptime_last_hour, hour_check_info, hour_post_check
from .last_day import uptime_last_day, day_check_info, day_post_check
from .last_week import uptime_last_week, week_check_info, week_post_check
from datetime import timezone, datetime
from tqdm.asyncio import tqdm
from typing import List
import asyncio

final_data: List[dict] = []


def is_business_hours(timestamp_utc: datetime, store_info: dict) -> bool:
    timestamp_utc = timestamp_utc.replace(tzinfo=timezone.utc)
    start_time_utc, end_time_utc = localize_date_time(
        timestamp_utc, store_info)
    return start_time_utc <= timestamp_utc <= end_time_utc


def calculate_uptime(log: dict, data: dict, store_report: dict) -> None:
    timestamp_utc = log['timestamp_utc'].replace(tzinfo=timezone.utc)
    status = log['status']
    if LAST_HOUR <= timestamp_utc <= CURRENT_TIME:
        # print("in last hour---")
        uptime_last_hour(data, store_report,
                         timestamp_utc, status)

    if LAST_DAY <= timestamp_utc <= CURRENT_TIME:
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

            uptime_last_day(data, store_report, timestamp_utc, status)
        else:
            uptime_last_day(data, store_report, timestamp_utc, status)

    if LAST_WEEK <= timestamp_utc <= CURRENT_TIME:

        if data['week']['end_time']:

            # If the time is in the other day's business hours
            while timestamp_utc > data['week']['end_time'][data['week']['idx']]:
                end_time = data['week']['end_time'][data['week']['idx']]
                data['week']['idx'] += 1
                uptime_last_week(data, store_report, end_time,
                                 data['week']['last_status'])
                # go to next day
                data['week']['last_timestamp'] = data['week']['start_time'][data['week']['idx']]

            uptime_last_week(data, store_report, timestamp_utc, status)


def get_store_info(business_hours: list, timezone_str: str) -> dict[int, dict]:
    store_info = {}
    for day_hours in business_hours:

        day = day_hours['day']
        store_info[day] = {}
        store_info[day]['start_time_utc'] = local_time_to_utc(
            day_hours['start_time_local'], timezone_str)
        store_info[day]['end_time_utc'] = local_time_to_utc(
            day_hours['end_time_local'], timezone_str)

    # If data is missing -> 24*7
    for day in range(0, 7):
        if day not in store_info:
            store_info[day] = {}
            store_info[day]['start_time_utc'] = datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
            store_info[day]['end_time_utc'] = datetime(
                2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    return store_info


async def fetch_store_info(store_id: int) -> dict[int, dict]:

    business_hours = await store_hours.find({'store_id': store_id}).to_list(length=None)

    store_timezone = await store_timezones.find_one({'store_id': store_id})
    timezone_str = store_timezone['timezone_str'] if store_timezone else 'America/Chicago'

    store_info = get_store_info(business_hours, timezone_str)

    return store_info


async def store_report(store_id: int) -> dict:
    store_report: dict = {
        'store_id': store_id,
        'uptime_last_hour': 0,
        'uptime_last_day': 0,
        'uptime_last_week': 0,
        'downtime_last_hour': 0,
        'downtime_last_day': 0,
        'downtime_last_week': 0
    }

    store_info: dict[int, dict] = await fetch_store_info(store_id)

    status_list = await store_status.find({'store_id': store_id}).sort('timestamp_utc', 1).to_list(length=None)

    data: dict = {
        'hour':
        {'last_timestamp': 0,
         'last_status': 'inactive',
         'total_time': 0
         },
        'day':
        {
            'last_timestamp': 0,
            'last_status': 'inactive',
            'total_time': 0,
            'start_time': [],
            'end_time': [],
            'idx': 0
        },
        'week':
        {
            'last_timestamp': 0,
            'last_status': 'inactive',
            'total_time': 0,
            'start_time': [],
            'end_time': [],
            'open_all_time': False,
            'idx': 0
        }
    }

    hour_check_info(data, store_report)
    day_check_info(store_info, data, store_report)
    week_check_info(store_info, data, store_report)

    for log in status_list:
        timestamp_utc = log['timestamp_utc']
        day = timestamp_utc.weekday()
        if day in store_info:
            if is_business_hours(timestamp_utc, store_info[day]):

                calculate_uptime(log, data, store_report)
        else:
            # Store runs 24*7 on that day
            calculate_uptime(log, data, store_report)

    hour_post_check(data, store_report)
    day_post_check(data, store_report)
    week_post_check(data, store_report)

    final_data.append(store_report)

    return store_report


async def generate_store_report() -> List[dict]:
    
    store_ids = await store_status.distinct('store_id')
    store_ids = store_ids[432:654]

    tasks = [asyncio.create_task(store_report(id)) for id in store_ids]
    for f in tqdm.as_completed(tasks, desc="Generating the Report"):
        await f
    
    await asyncio.gather(*tasks)

    return final_data
