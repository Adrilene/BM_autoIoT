from main import db

from datetime import datetime

from models.SmartTvCommandSensorData import SmartTvCommandSensorData

from models.SmartTv import *

import re

class SmartTvCommandSensor(db.Model):
        
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    send_interval = db.Column(db.String)

    smart_tv_id = db.Column(db.Integer, db.ForeignKey("smart_tv.id"))

    metrics = db.relationship("SmartTvCommandSensorData", backref="smart_tv_command_sensor", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return "<SmartTvCommandSensor {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def change_status(self, status):
        
        new_metric = SmartTvCommandSensorData(smart_tv_command_sensor=self)

        new_metric.status = status

        db.session.add(new_metric)
        db.session.commit()
        
    def show_message(self, notification):
        print("\nFrom SmarTv")
        print("Notification Received!")
        print(notification, '\n')
        return 1 

    def show_command(self, new_metric):
        print("\nFrom SmarTv")
        print("Command Received:")
        print(new_metric.command, '\n')

    def receive_commands(self, command):
        if 'status' in command.lower():
            if 'true' in command.lower():
                self.change_status(True)
            elif 'false' in command.lower():
                self.change_status(False)
            return 1
        elif 'message' in command.lower():
            get_notification = command.lower()[8:]
            return self.show_message(get_notification)
        else:
            print('Command not recognized!')
            return 0

    def add_metric(self, command, caller):
        if 'SmartPhone' in str(caller):
            new_metric = SmartTvCommandSensorData(smart_tv_command_sensor=self)

            new_metric.command = command
            if self.receive_commands(new_metric.command): 
                self.show_command(new_metric)
            else:
                return False
            db.session.add(new_metric)
            db.session.commit()

            return True
        return False

    def add_metric_from_dict(self, D):
        try:
            new_metric = SmartTvCommandSensorData(smart_tv_command_sensor=self)

            #print(D)

            for k, v in D.items():
                #if type(getattr(SmartTvCommandSensorData, k)) == property :
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
        metrics = self.metrics.filter(getattr(SmartTvCommandSensorData, metric_name) != None).order_by(SmartTvCommandSensorData.created_at.desc()).limit(30).all()

        if axis == 'x':
            result = [metric.created_at.isoformat() for metric in metrics]
        else:
            result = [getattr(metric, metric_name) for metric in metrics]

        return result

    def get_last_metric_data(self, metric_name):
        
        if not hasattr(SmartTvCommandSensorData, metric_name):
            return None
        
        metric = self.metrics.filter(getattr(SmartTvCommandSensorData, metric_name) != None).order_by(SmartTvCommandSensorData.created_at.desc()).first()

        return metric