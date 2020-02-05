from main import db

from datetime import datetime

from geoalchemy2 import Geometry


class MonitorCryingSensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    crying = db.Column(db.Boolean)


    monitor_crying_sensor_id = db.Column(db.Integer, db.ForeignKey("monitor_crying_sensor.id"))

    def __repr__(self):
        return "<MonitorCryingSensorData {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

