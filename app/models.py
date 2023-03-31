from mongoengine import Document, IntField, FloatField, StringField, DateTimeField, EmbeddedDocument, ListField, EmbeddedDocumentField

class StoreData(EmbeddedDocument):
    store_id = IntField(required=True)
    uptime_last_hour = FloatField(required=True)
    uptime_last_day = FloatField(required=True)
    uptime_last_week = FloatField(required=True)
    downtime_last_hour = FloatField(required=True)
    downtime_last_day = FloatField(required=True)
    downtime_last_week = FloatField(required=True)


class Report(Document):
    report_id = StringField(unique=True)
    report_data = ListField(EmbeddedDocumentField(StoreData), required=True)

    meta = {'collection': 'reports'}


class StoreStatus(Document):
    store_id = IntField()
    status = StringField()
    timestamp_utc = DateTimeField()

    meta = {'collection': 'store_status'}


class StoreHours(Document):
    store_id = IntField()
    day = IntField()
    start_time_local = StringField()
    end_time_local = StringField()

    meta = {'collection': 'store_hours'}

class StoreTimezone(Document):
    store_id = IntField()
    timezone_str = StringField()
    
    meta = {'collection': 'store_timezones'}
