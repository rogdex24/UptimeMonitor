from fastapi import FastAPI
from fastapi.responses import RedirectResponse, StreamingResponse
from config.database import connect, reports
from report import generate_report, report_status, generate_csv
import asyncio
import uuid

app = FastAPI()
connect(db="loop", host="localhost", port=27017)

@app.get("/", include_in_schema=False)
def redirect_root():
    return RedirectResponse(url='/docs')

@app.get('/trigger_report')
async def trigger_report():
    """_summary_

    Returns:
        report_id (str): unique report_id
    """
    report_id = str(uuid.uuid4())
    asyncio.create_task(generate_report(report_id))

    return {'report_id': report_id}


@app.get('/get_report/{report_id}')
async def get_report(report_id: str):
    """_summary_

    Args:
        report_id (str): unique report_id

    Returns:
        CSV_File: Report in a csv file
    """
    status = report_status(report_id)
    if report_status(report_id) == 'Running':
        return {"message": status}
    else:
        result = await reports.find_one({"report_id": report_id})
        if result:
            csv_file = generate_csv(result['report_data'])
            response = StreamingResponse(iter([csv_file.getvalue()]), media_type="text/csv")
            response.headers["Content-Disposition"] = f"attachment;filename={report_id[:5]}.csv"
            return response
        else:
            return {"message": "Invalid report_id"}

