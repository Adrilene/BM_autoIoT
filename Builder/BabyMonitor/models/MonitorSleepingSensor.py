from main import db

from datetime import datetime


from models.MonitorSleepingSensorData import MonitorSleepingSensorData

class MonitorSleepingSensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    send_interval = db.Column(db.String)

    monitor_id = db.Column(db.Integer, db.ForeignKey("monitor.id"))

    metrics = db.relationship("MonitorSleepingSensorData", backref="monitor_sleeping_sensor", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return "<MonitorSleepingSensor {}>".format(self.id)

    def created(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")

    def add_metric(self, sleeping):
        new_metric = MonitorSleepingSensorData(monitor_sleeping_sensor=self)

        new_metric.sleeping = sleeping

        db.session.add(new_metric)
        db.session.commit()

    def add_metric_from_dict(self, D):
        try:
            new_metric = MonitorSleepingSensorData(monitor_sleeping_sensor=self)

            print(D)

            for k, v in D.items():
                #if type(getattr(MonitorSleepingSensorData, k)) == property :
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
        metrics = self.metrics.filter(getattr(MonitorSleepingSensorData, metric_name) != None).order_by(MonitorSleepingSensorData.created_at.desc()).limit(30).all()

        if axis == 'x':
            result = [metric.created_at.isoformat() for metric in metrics]
        else:
            result = [getattr(metric, metric_name) for metric in metrics]

        return result

    def get_last_metric_data(self, metric_name):
        
        if not hasattr(MonitorSleepingSensorData, metric_name):
            return None
        
        metric = self.metrics.filter(getattr(MonitorSleepingSensorData, metric_name) != None).order_by(MonitorSleepingSensorData.created_at.desc()).first()

        return metric