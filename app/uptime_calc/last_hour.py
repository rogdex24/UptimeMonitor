from utils.constants import CURRENT_TIME, LAST_HOUR
from utils.util import get_duration
from datetime import datetime, timedelta

def uptime_last_hour(data: dict, store_report: dict, current_time: datetime, status: str) -> None:
    if status == 'inactive':

        duration = get_duration(
            data['hour']['last_timestamp'], current_time)
        store_report['uptime_last_hour'] -= duration

    data['hour']['last_timestamp'] = current_time
    data['hour']['last_status'] = status


def hour_check_info(data: dict, store_report: dict) -> None:

    data['hour']['last_timestamp'] = LAST_HOUR
    data['hour']['total_time'] = timedelta(minutes=60)
    store_report['uptime_last_hour'] = timedelta(minutes=60)


def hour_post_check(data: dict, store_report: dict) -> None:

    # if the last status is inactive make the rest of the time inactive as well
    uptime_last_hour(data, store_report, CURRENT_TIME, data['hour']['last_status'])

    store_report['downtime_last_hour'] = data['hour']['total_time'] - \
        store_report['uptime_last_hour']

    for key in ['uptime_last_hour', 'downtime_last_hour']:
        if isinstance(store_report[key], timedelta):
            store_report[key] = round(store_report[key].total_seconds() / 60, 2)