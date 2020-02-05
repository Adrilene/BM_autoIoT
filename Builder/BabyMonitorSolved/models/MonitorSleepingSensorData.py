from main import db

from datetime import datetime

from geoalchemy2 import Geometry


class MonitorSleepingSensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sleeping = db.Column(db.Boolean)


    monitor_sleeping_sensor_id = db.Column(db.Integer, db.ForeignKey("monitor_sleeping_sensor.id"))

    def __repr__(self):
        return "<MonitorSleepingSensorData {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

