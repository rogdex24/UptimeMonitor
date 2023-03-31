from models import Report, StoreData
from uptime_calc.store_report import generate_store_report
from typing import List
from io import StringIO
import csv

report_completed = {}


def report_status(report_id: str) -> str:
    if report_id in report_completed:
        if report_completed[report_id] == False:
            return 'Running'
        else:
            return 'Completed'
    else:
        return 'NULL'


async def generate_report(report_id: str) -> None:
    
    print("--> Report Generation Started")
    report_completed[report_id] = False
    
    try:
        final_data = await generate_store_report()
    except Exception as e:
        print("Report Generation Failed", e)
        del report_completed[report_id]

    # Create a list of StoreData objects
    store_data_list = []
    for store_data in final_data:
        store_data_obj = StoreData(**store_data)
        store_data_list.append(store_data_obj)

    # Create a Report object with the list of StoreData objects
    report = Report(
        report_id=report_id,
        report_data=store_data_list
    )

    # Save the report to the database
    report.save()
    
    print("--> Report Succesfully Generated !")

    report_completed[report_id] = True



def generate_csv(report_data: List) -> StringIO:
    csv_file = StringIO()
    fieldnames = report_data[0].keys()
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for row in report_data:
        writer.writerow(row)

    return csv_file
