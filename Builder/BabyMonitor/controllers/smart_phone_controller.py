from flask_login import login_required, login_user
from flask import Blueprint, redirect, url_for, g, render_template, request, flash
from forms.FormLogin import FormLogin

from sqlalchemy.orm.attributes import InstrumentedAttribute
from models.SmartPhone import SmartPhone

from main import db


smart_phone_template = Blueprint("smart_phone_template", __name__, template_folder='templates')

@smart_phone_template.route('/dashboard/smart_phone/<int:id>')
def dashboard(id):
    '''
    Dashboard with information about list of devices.
    :param id: smart_phone id
    :return: Render the HTML page
    '''
    
    smart_phone = SmartPhone.query.filter_by(id=id).first()
    list_of_attrs = []
    list_of_sensors = []
    for k, v in vars(SmartPhone).items():
        if (type(v) == InstrumentedAttribute):
            if('_sensor' in k):
                list_of_sensors.append(k)
            else:
                list_of_attrs.append(k)        
    return render_template('dashboard_smart_phone.html', smart_phone=smart_phone, list_of_attrs = list_of_attrs, list_of_sensors = list_of_sensors)        
    


@smart_phone_template.route('/smart_phone_list')
@login_required
def list():
    '''
    Returns information about the types of sensors.
    :return: Renders sensors list.
    '''
    models = SmartPhone.query.all()

    list_of_attrs = []
    list_of_sensors = []
    for k, v in vars(SmartPhone).items():
        if (type(v) == InstrumentedAttribute):

            if('_sensor' in k):
                list_of_sensors.append(k)
            else:
                list_of_attrs.append(k)

    return render_template('smart_phone_list.html',models=models, list_of_attrs=list_of_attrs, list_of_sensors=list_of_sensors)

@smart_phone_template.route('/delete/smart_phone/<int:id>')
@login_required
def delete(id):
    '''
    Deletes a smart_phone object from the database.
    :param id: smart_phone object id.
    :return: Redirects to List Page.
    '''
    selected_object = SmartPhone.query.filter_by(id=id).first()

    if (selected_object):
        db.session.delete(selected_object)
        db.session.commit()

        flash('SmartPhone deleted successfully.', 'success')
        return redirect(url_for('smart_phone_template.list'))

    flash('Error deleting the SmartPhone.', 'danger')
    return redirect(url_for('smart_phone_template.list'))