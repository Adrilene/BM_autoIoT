from flask_login import login_required, login_user
from flask import Blueprint, redirect, url_for, g, render_template, request, flash
from forms.FormLogin import FormLogin

from sqlalchemy.orm.attributes import InstrumentedAttribute
from models.SmartTv import SmartTv

from main import db


smart_tv_template = Blueprint("smart_tv_template", __name__, template_folder='templates')

@smart_tv_template.route('/dashboard/smart_tv/<int:id>')
def dashboard(id):
    '''
    Dashboard with information about list of devices.
    :param id: smart_tv id
    :return: Render the HTML page
    '''
    
    smart_tv = SmartTv.query.filter_by(id=id).first()
    list_of_attrs = []
    list_of_sensors = []
    for k, v in vars(SmartTv).items():
        if (type(v) == InstrumentedAttribute):
            if('_sensor' in k):
                list_of_sensors.append(k)
            else:
                list_of_attrs.append(k)        
    return render_template('dashboard_smart_tv.html', smart_tv=smart_tv, list_of_attrs = list_of_attrs, list_of_sensors = list_of_sensors)        
    


@smart_tv_template.route('/smart_tv_list')
@login_required
def list():
    '''
    Returns information about the types of sensors.
    :return: Renders sensors list.
    '''
    models = SmartTv.query.all()

    list_of_attrs = []
    list_of_sensors = []
    for k, v in vars(SmartTv).items():
        if (type(v) == InstrumentedAttribute):

            if('_sensor' in k):
                list_of_sensors.append(k)
            else:
                list_of_attrs.append(k)

    return render_template('smart_tv_list.html',models=models, list_of_attrs=list_of_attrs, list_of_sensors=list_of_sensors)

@smart_tv_template.route('/delete/smart_tv/<int:id>')
@login_required
def delete(id):
    '''
    Deletes a smart_tv object from the database.
    :param id: smart_tv object id.
    :return: Redirects to List Page.
    '''
    selected_object = SmartTv.query.filter_by(id=id).first()

    if (selected_object):
        db.session.delete(selected_object)
        db.session.commit()

        flash('SmartTv deleted successfully.', 'success')
        return redirect(url_for('smart_tv_template.list'))

    flash('Error deleting the SmartTv.', 'danger')
    return redirect(url_for('smart_tv_template.list'))