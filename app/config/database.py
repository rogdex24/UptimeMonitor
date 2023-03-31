from mongoengine import connect
# from pymongo import MongoClient

# client = MongoClient("mongodb://localhost:27017/")
# db = client["loop"]
# reports = db["reports"]
# store_status = db["store_status"]
# store_hours = db["store_hours"]
# store_timezones = db["store_timezones"]

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
db = client['loop']
reports = db["reports"]
store_hours = db['store_hours']
store_status = db['store_status']
store_timezones = db['store_timezones']