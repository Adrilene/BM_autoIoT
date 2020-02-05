from flask_login import login_required, login_user
from flask import Blueprint, redirect, url_for, g, render_template, request, flash
from forms.FormLogin import FormLogin

from sqlalchemy.orm.attributes import InstrumentedAttribute
from models.Monitor import Monitor

from main import db


monitor_template = Blueprint("monitor_template", __name__, template_folder='templates')

@monitor_template.route('/dashboard/monitor/<int:id>')
def dashboard(id):
    '''
    Dashboard with information about list of devices.
    :param id: monitor id
    :return: Render the HTML page
    '''
    
    monitor = Monitor.query.filter_by(id=id).first()
    list_of_attrs = []
    list_of_sensors = []
    for k, v in vars(Monitor).items():
        if (type(v) == InstrumentedAttribute):
            if('_sensor' in k):
                list_of_sensors.append(k)
            else:
                list_of_attrs.append(k)        
    return render_template('dashboard_monitor.html', monitor=monitor, list_of_attrs = list_of_attrs, list_of_sensors = list_of_sensors)        
    


@monitor_template.route('/monitor_list')
@login_required
def list():
    '''
    Returns information about the types of sensors.
    :return: Renders sensors list.
    '''
    models = Monitor.query.all()

    list_of_attrs = []
    list_of_sensors = []
    for k, v in vars(Monitor).items():
        if (type(v) == InstrumentedAttribute):

            if('_sensor' in k):
                list_of_sensors.append(k)
            else:
                list_of_attrs.append(k)

    return render_template('monitor_list.html',models=models, list_of_attrs=list_of_attrs, list_of_sensors=list_of_sensors)

@monitor_template.route('/delete/monitor/<int:id>')
@login_required
def delete(id):
    '''
    Deletes a monitor object from the database.
    :param id: monitor object id.
    :return: Redirects to List Page.
    '''
    selected_object = Monitor.query.filter_by(id=id).first()

    if (selected_object):
        db.session.delete(selected_object)
        db.session.commit()

        flash('Monitor deleted successfully.', 'success')
        return redirect(url_for('monitor_template.list'))

    flash('Error deleting the Monitor.', 'danger')
    return redirect(url_for('monitor_template.list'))