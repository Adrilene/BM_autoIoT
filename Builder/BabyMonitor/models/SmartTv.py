from main import db

from datetime import datetime

from models.SmartTvCommandSensor import SmartTvCommandSensor

class SmartTv(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    barcode = db.Column(db.String)
    name = db.Column(db.String)
    key = db.Column(db.String, unique=True, nullable=False)
    status = False
    income_command = False

    command_sensor_sensor = db.relationship("SmartTvCommandSensor", uselist=False, backref="smart_tv", cascade="all, delete-orphan")

    def get_tv(self, caller):
        if 'SmartPhone' in str(caller):
            return self
        else:
            print("Unauthorized!")
            return None

    def __repr__(self):
        return "<SmartTv {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def init_sensors(self):
        if self.id is None:
            db.session.add(self)
            db.session.flush()

        if self.command_sensor_sensor is None:
            self.command_sensor_sensor = SmartTvCommandSensor( smart_tv = self)

        db.session.commit()