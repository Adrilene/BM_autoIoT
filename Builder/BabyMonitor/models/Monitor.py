from main import db

from datetime import datetime

from models.MonitorBreathingSensor import MonitorBreathingSensor
from models.MonitorSleepingSensor import MonitorSleepingSensor
from models.MonitorCryingSensor import MonitorCryingSensor

class Monitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    name = db.Column(db.String)
    barcode = db.Column(db.String)
    key = db.Column(db.String, unique=True, nullable=False)

    breathing_sensor_sensor = db.relationship("MonitorBreathingSensor", uselist=False, backref="monitor", cascade="all, delete-orphan")
    sleeping_sensor_sensor = db.relationship("MonitorSleepingSensor", uselist=False, backref="monitor", cascade="all, delete-orphan")
    crying_sensor_sensor = db.relationship("MonitorCryingSensor", uselist=False, backref="monitor", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Monitor {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def init_sensors(self):
        if self.id is None:
            db.session.add(self)
            db.session.flush()

        if self.breathing_sensor_sensor is None:
            self.breathing_sensor_sensor = MonitorBreathingSensor( monitor = self)
        if self.sleeping_sensor_sensor is None:
            self.sleeping_sensor_sensor = MonitorSleepingSensor( monitor = self)
        if self.crying_sensor_sensor is None:
            self.crying_sensor_sensor = MonitorCryingSensor( monitor = self)

        db.session.commit()
