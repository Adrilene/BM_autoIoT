from flask import request, Flask
from flask_socketio import Namespace, emit, SocketIO
import json
import paho.mqtt.client as mqtt

from threading import Lock

thread = None
thread_lock = Lock()

count = 0

def background_thread(_socketio : SocketIO, _current_app : Flask, _namespace):
    """Example of how to send server generated events to clients."""


    def on_connect(client, userdata, flags, rc):
        print("Connected with result code in " + str(rc) + ' SmartPhone')

        #client.subscribe('baby_monitor_project/data/smart_phone')

    def on_message(client, userdata, message):
        data = json.loads(message.payload)
        _socketio.emit('data_smart_phone',
                       {'message': 'New data from SmartPhone', 'data': data},
                       namespace=_namespace)
    try:

        app = _current_app

        client = mqtt.Client(client_id='Baby Monitor ProjectSmartPhone')

        client.on_connect = on_connect
        client.on_message = on_message

        if (app.config['MQTT_USERNAME'] != '' and app.config['MQTT_PASSWORD'] != ''):
            client.username_pw_set(app.config['MQTT_USERNAME'],
                                        password=app.config['MQTT_PASSWORD'])

        client.connect(app.config['MQTT_BROKER_URL'],
                           app.config['MQTT_BROKER_PORT'])

        client.loop_forever()

    except Exception as e:
        print('Error inside background thread', e)
        
        

class SmartPhoneSocket(Namespace):

    def __init__(self, app, namespace):
        super(Namespace, self).__init__(namespace)
        self.app = app

    def on_connect(self):
        
        global thread
        with thread_lock:
            if thread is None:
                thread = self.socketio.start_background_task(
                    background_thread, self.socketio, self.app, self.namespace)
        emit('data_smart_phone', {'message': 'Connected', 'count': 0})
    


    def on_disconnect(self):
        
        print('Client disconnected', request.sid)
    