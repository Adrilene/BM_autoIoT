from main import db

from datetime import datetime

from geoalchemy2 import Geometry


class SmartPhoneNotificationSensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notification = db.Column(db.String)


    smart_phone_notification_sensor_id = db.Column(db.Integer, db.ForeignKey("smart_phone_notification_sensor.id"))

    def __repr__(self):
        return "<SmartPhoneNotificationSensorData {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

