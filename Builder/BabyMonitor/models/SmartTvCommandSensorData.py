from main import db

from datetime import datetime

from geoalchemy2 import Geometry

class SmartTvCommandSensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    command = db.Column(db.String)
    status = db.Column(db.Boolean)
    aplication = db.Column(db.String)        

    smart_tv_command_sensor_id = db.Column(db.Integer, db.ForeignKey("smart_tv_command_sensor.id"))

    def __repr__(self):
        return "<SmartTvCommandSensorData {}>".format(self.id)
        
    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")