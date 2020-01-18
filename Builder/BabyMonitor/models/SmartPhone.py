from main import db

from datetime import datetime

from models.SmartPhoneNotificationSensor import SmartPhoneNotificationSensor


class SmartPhone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    barcode = db.Column(db.String)
    name = db.Column(db.String)
    key = db.Column(db.String, unique=True, nullable=False)

    notification_sensor_sensor = db.relationship("SmartPhoneNotificationSensor", uselist=False, backref="smart_phone", cascade="all, delete-orphan")

    def __repr__(self):
        return "<SmartPhone {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def init_sensors(self):
        if self.id is None:
            db.session.add(self)
            db.session.flush()

        if self.notification_sensor_sensor is None:
            self.notification_sensor_sensor = SmartPhoneNotificationSensor( smart_phone = self)

        db.session.commit()

