from datetime import datetime, timedelta
from typing import Tuple
import pytz


def local_time_to_utc(local_time_str: str, tz_str: str) -> datetime:
    """
    Convert a local time string to UTC.

    :param local_time_str: The local time string in the format '%H:%M:%S'.
    :param tz_str: The timezone string.
    :return: The converted UTC time as a datetime object.
    """
    input_dt = f"2023-01-25 {local_time_str}"
    local = pytz.timezone(tz_str)
    naive = datetime.strptime(input_dt, "%Y-%m-%d %H:%M:%S")
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(pytz.utc)
    utc_time = utc_dt

    return utc_time


def localize_date_time(date_obj: datetime, time_obj: datetime) -> Tuple[datetime, datetime]:
    """
    Update the date of [start, end] intervals in time_obj with the date of date_obj.

    Args:
        date_obj (datetime): A datetime object representing the date to be combined.
        time_obj (datetime): A datetime object representing the time range to be combined.
            This object should have two attributes:
            - start_time_utc: A datetime object representing the start time of the range in UTC timezone.
            - end_time_utc: A datetime object representing the end time of the range in UTC timezone.

    Returns:
        Tuple[datetime, datetime]: A tuple containing two datetime objects in the same timezone as the input time range,
        representing the localized start and end times.
    """
    start_time = time_obj['start_time_utc'].time()
    end_time = time_obj['end_time_utc'].time()
    start_date = end_date = date_obj.date()

    if end_time <= start_time:

        end_date = start_date + timedelta(days=1)

    new_start_dt = datetime.combine(start_date, start_time).replace(
        tzinfo=time_obj['start_time_utc'].tzinfo)
    new_end_dt = datetime.combine(end_date, end_time).replace(
        tzinfo=time_obj['end_time_utc'].tzinfo)

    return new_start_dt, new_end_dt


def get_duration(start_time: datetime, end_time: datetime) -> timedelta:
    """
    Calculates the duration b/w start and end time.
    s
    Args:
        start_time (datetime): start time of the interval
        end_time (datetime): end time of the interval

    Returns:
        timedelta: Duration b/w start and end
    """
    duration = end_time - start_time
    return duration
