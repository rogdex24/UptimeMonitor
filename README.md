# Uptime Monitor

## Project Description

This project aims to generate a real time report on store uptime for a set of stores based on data collected from multiple sources. 

The report generated by this project includes data about the uptime and downtime for each store within the specified time intervals, extrapolated based on periodic polls ingested. The report only includes observations within business hours and is output in CSV format with the specified schema.

Overall, this project is designed to efficiently and accurately provide store uptime and downtime information to the user in a clear and understandable way.


## Tech Stack 

This project is implemented using the Python programming language and the FastAPI web framework for building the web API. MongoDB is used as the database to store the data for this project.

The code is designed to be asynchronous, taking advantage of Python's async/await syntax for handling concurrent tasks. This allows for efficient handling of large amounts of data, such as polling every store every hour and processing their uptime and downtime.

## Data Sources

We will have three sources of data as MongoDB Collections:

1. **Store status:** We poll every store roughly every hour and have data about whether the store was active or not in a collection. The collection has 3 columns (`store_id`, `timestamp_utc`, `status`) where status is active or inactive. All timestamps are in UTC.

2. **Business hours:** We have the business hours of all the stores - schema of this data is `store_id`, `dayOfWeek` (0=Monday, 6=Sunday), `start_time_local`, `end_time_local`. These times are in the local time zone. If data is missing for a store, assume it is open 24*7.

3. **Timezone for the stores:** Schema is `store_id`, `timezone_str`. If data is missing for a store, assume it is America/Chicago. This is used so that data sources 1 and 2 can be compared against each other.

All these collections are named `store_status`, `store_hours`, `store_timezones`, respectively.

## Data Output Description

Output's a report as a CSV file to the user that has the following schema:

`store_id`, `uptime_last_hour` (in minutes), `uptime_last_day` (in hours), `update_last_week` (in hours), `downtime_last_hour` (in minutes), `downtime_last_day` (in hours), `downtime_last_week` (in hours)

1. Uptime and downtime include only the observations within business hours.
2. Uptime and downtime are extrapolated based on the periodic polls we have ingested, to the entire time interval.

## API Description

We need two APIs:

1. `/trigger_report` endpoint that will trigger report generation from the data provided (stored in DB)
    1. No input 
    2. Output - `report_id` (random string) 
    3. `report_id` will be used for polling the status of report completion
2. `/get_report` endpoint that will return the status of the report or the CSV
    1. Input - `report_id`
    2. Output
        - If report generation is not complete, returns “Running” as the output.
        - If report generation is complete, returns the CSV file with the schema described above.
