from datetime import datetime, timedelta

# Max Timestamp among all the observations in UTC
CURRENT_TIME = datetime.strptime(
    '2023-01-25 18:13:22.479000+00:00', '%Y-%m-%d %H:%M:%S.%f%z')

LAST_HOUR = CURRENT_TIME - timedelta(hours=1) 
# "2023-01-25 17:13:22"
LAST_DAY = CURRENT_TIME - timedelta(days=1) 
# "2023-01-24 18:13:22"
LAST_WEEK = CURRENT_TIME - timedelta(weeks=1)
# "2023-01-18 18:13:22"
