from flask import Flask, Blueprint, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import configuration
from flask_login import LoginManager, current_user
import importlib
from flask_restless import APIManager
#from flask_restless_swagger import SwagAPIManager as APIManager

from flask_socketio import SocketIO


import os
import sys

CONFIGURATION = 'development'

# Creating the main app object
app = Flask(__name__)

# Load configuration from the config file
app.config.from_object(configuration[CONFIGURATION])
configuration[CONFIGURATION].init_app(app)


# Initializing the Flask Modules
db = SQLAlchemy(app) # Manage the communication with the database
migrate = Migrate(app, db) # Helps to migrate and upgrade the database
api = APIManager(app, flask_sqlalchemy_db=db) # Automatically create API for each database object

# Give access to low latency bi-directional communications between the clients and the server.
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)

def register_blueprints(app):
    '''
    Register all available blueprints in the "controller" folder.
    :param app: the flask application
    :return: None
    '''
    from werkzeug.utils import find_modules, import_string

    for name in find_modules('controllers'):
        if name not in sys.modules:
            mod = importlib.import_module(name)

            for attr in dir(mod):
                #print(attr)
                if type(getattr(mod, attr)) == Blueprint:
                    app.register_blueprint(getattr(mod, attr))

# LoginManager handle login and logout
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'users_template.login'

@lm.user_loader
def load_user(id):
    '''
    Load and return data from the table by using user id.
    :param id: user id
    :return: User object
    '''
    from models.User import User
    return User.query.get(int(id))

@app.before_request
def before_app_request():
    '''
    This function runs before each request to the application
    :return:
    '''
    session.modified = True
    g.user = current_user

if __name__ == '__main__':

    # MQTTManager is responsible for managing all communication with the MQTT Broker
    from MQTTManager import MQTTManager
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        mqttManager = MQTTManager()
        mqttManager.start()

    # MonitorSocket manages web socket communication between client and server
    from sockets import MonitorSocket
    socketio.on_namespace(MonitorSocket(app, "/data_monitor"))



    # Automatically generates an API based on Monitor model
    from models import Monitor
    api.create_api(Monitor, methods=['GET', 'POST', 'DELETE'], primary_key='key')

    # Automatically generates an API based on MonitorBreathingSensor model
    from models import MonitorBreathingSensor
    api.create_api(MonitorBreathingSensor, methods=['GET', 'POST', 'DELETE']
                   )

    # Automatically generates an API based on MonitorBreathingSensorData model
    from models import MonitorBreathingSensorData
    api.create_api(MonitorBreathingSensorData, methods=['GET', 'POST', 'DELETE']
                  )

    # Automatically generates an API based on MonitorSleepingSensor model
    from models import MonitorSleepingSensor
    api.create_api(MonitorSleepingSensor, methods=['GET', 'POST', 'DELETE']
                   )

    # Automatically generates an API based on MonitorSleepingSensorData model
    from models import MonitorSleepingSensorData
    api.create_api(MonitorSleepingSensorData, methods=['GET', 'POST', 'DELETE']
                  )

    # Automatically generates an API based on MonitorCryingSensor model
    from models import MonitorCryingSensor
    api.create_api(MonitorCryingSensor, methods=['GET', 'POST', 'DELETE']
                   )

    # Automatically generates an API based on MonitorCryingSensorData model
    from models import MonitorCryingSensorData
    api.create_api(MonitorCryingSensorData, methods=['GET', 'POST', 'DELETE']
                  )



    # Register blueprints
    register_blueprints(app)

    # Run the application on the specified host and port 5000
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        mqttManager.stop()
