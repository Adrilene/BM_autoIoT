from main import db

from datetime import datetime
import random
import time

from models.SmartPhoneNotificationSensorData import SmartPhoneNotificationSensorData

class SmartPhoneNotificationSensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    send_interval = db.Column(db.String)

    smart_phone_id = db.Column(db.Integer, db.ForeignKey("smart_phone.id"))

    metrics = db.relationship("SmartPhoneNotificationSensorData", backref="smart_phone_notification_sensor", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return "<SmartPhoneNotificationSensor {}>".format(self.id)
        #return getattr(self,attr)
    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def show_notification(self, new_metric):
        print("\nFrom SmartPhone")
        print("Notification Received!")
        print(new_metric.notification, '\n')

    def add_metric(self, notification, connection):
        waitTime = random.randint(1,8)
        #time.sleep(waitTime)
        print(waitTime)
        if connection >= 1 or waitTime < 5:
            new_metric = SmartPhoneNotificationSensorData(smart_phone_notification_sensor=self)

            new_metric.notification = notification
            self.show_notification(new_metric)

            db.session.add(new_metric)
            db.session.commit()
            
            return 1
        else: 
            return 0

    def add_metric_from_dict(self, D):
        try:
            new_metric = SmartPhoneNotificationSensorData(smart_phone_notification_sensor=self)

            print(D)

            for k, v in D.items():
                #if type(getattr(SmartPhoneNotificationSensorData, k)) == property :
                if hasattr(new_metric, k + '_raw_point_x'):
                    print('Probably a position attr. Trying to set as a POINT attr.')

                    k = k + '_raw_point'

                    x, y = v.split(',')
                    x.strip()
                    y.strip()

                    setattr(new_metric, k + '_x', float(x))
                    setattr(new_metric, k + '_y', float(y))
                else:
                    setattr(new_metric, k, v)

            db.session.add(new_metric)
            db.session.commit()
        except Exception as e:
            print('Error inserting metric!', e)

    def number_of_metrics(self):
        return self.metrics.count()

    def get_metrics_to_plot(self, axis, metric_name):
        metrics = self.metrics.filter(getattr(SmartPhoneNotificationSensorData, metric_name) != None).order_by(SmartPhoneNotificationSensorData.created_at.desc()).limit(30).all()

        if axis == 'x':
            result = [metric.created_at.isoformat() for metric in metrics]
        else:
            result = [getattr(metric, metric_name) for metric in metrics]

        return result

    def get_last_metric_data(self, metric_name):
        
        if not hasattr(SmartPhoneNotificationSensorData, metric_name):
            return None
        
        metric = self.metrics.filter(getattr(SmartPhoneNotificationSensorData, metric_name) != None).order_by(SmartPhoneNotificationSensorData.created_at.desc()).first()

        return metric