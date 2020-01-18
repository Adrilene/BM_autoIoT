import paho.mqtt.client as mqtt
import threading
import json
import time
import random

from models import *

from config import configuration

CONFIGURATION = 'development'     

#MQTT Manager

def on_connect(client, userdata, flags, rc):
    '''
        This method is triggered when the application connects with the MQTT Broker.
    :param client: MQTT client
    :param userdata:
    :param flags:
    :param rc: Connection status code
    :return: None.
    '''

    print("Connected with result code " + str(rc))

    # Subscribe to topics
    client.subscribe('baby_monitor_project/register/monitor')
    client.subscribe('baby_monitor_project/update/monitor')
    client.subscribe('baby_monitor_project/data/monitor')

def baby_monitor_project_register_monitor(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/register/monitor"
    '''
    
    try:
        message = json.loads(msg.payload)
        device = Monitor.query.filter_by(key=message['key']).first()
    
        if not device: #Device is not in the database
            print('Creating new device.')
            device = Monitor()
            device.key = message['key']
    
            
            if 'name' in message:
                device.name = message['name']
            
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'key' in message:
                device.key = message['key']
            
    
            db.session.add(device)
            db.session.commit()
    
            device.init_sensors()
        else:
            print('Device already in the database.')
    
    except Exception as e:
        print(e)
            
def baby_monitor_project_update_monitor(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/update/monitor"
    '''
    
    try:
        message = json.loads(msg.payload)
        device = Monitor.query.filter_by(key=message['key']).first()
    
        if device: #Device in the database
            print('Updating device.')
            
            device.key = message['key']
    
            
            if 'name' in message:
                device.name = message['name']
            
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'key' in message:
                device.key = message['key']
            
    
            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database
            print('Device not in the database.')
    
    except Exception as e:
        print(e) 

maxNoChanges = random.randint(1,20) 
choice = random.choices([True, False], [0.75, 0.25], k = 1)[0]
changes = 0 

def makeChoices():
    global maxNoChanges, choice, changes

    if changes >= maxNoChanges: 
        maxNoChanges = random.randint(1,20)
        changes = 0
        choice = random.choices([True, False], [0.75, 0.25], k = 1)[0]
    else:  
        changes += 1

    print("Max: {}. Changes: {}.".format(maxNoChanges, changes))
        
def baby_monitor_project_data_monitor(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/data/monitor"
    '''
    
    try:
        global choice, changes
        message = json.loads(msg.payload)
        device = Monitor.query.filter_by(key=message['key']).first()
    
        if device: #Device in the database
            print('Adding data to device.')                
    
            if 'breathing_sensor_sensor' in message:
                
                makeChoices()
                message['breathing_sensor_sensor']['breathing'] = choice
               
                if not choice:
                    message['breathing_sensor_sensor']['time_no_breathing'] = changes
                
                else:
                    message['breathing_sensor_sensor']['time_no_breathing'] = 0 
                
                if message['breathing_sensor_sensor']['time_no_breathing'] > 15:
                    print('Alert parents!')

                if not message['breathing_sensor_sensor']['breathing']:
                    count = 0

                device.breathing_sensor_sensor.add_metric_from_dict(message['breathing_sensor_sensor'])

            if 'sleeping_sensor_sensor' in message:
                device.sleeping_sensor_sensor.add_metric_from_dict(message['sleeping_sensor_sensor'])
            
            if 'crying_sensor_sensor' in message:
                message['crying_sensor_sensor']['crying'] = not message['sleeping_sensor_sensor']['sleeping']

                device.crying_sensor_sensor.add_metric_from_dict(message['crying_sensor_sensor'])
        
            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database
            print('Device not in the database.')
    
    except Exception as e:
        print(e)
            

#MQTT Manager class responsible for the communication between application and MQTT Broker.
class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client(client_id='Baby Monitor Project.1578327599.3277664')

    def start_mqtt_thread(self):
        self.client.on_connect = on_connect

        if (configuration[CONFIGURATION].MQTT_USERNAME != '' and configuration[
            CONFIGURATION].MQTT_PASSWORD != ''):
            self.client.username_pw_set(configuration[CONFIGURATION].MQTT_USERNAME,
                                        password=configuration[CONFIGURATION].MQTT_PASSWORD)

        self.client.connect(configuration[CONFIGURATION].MQTT_BROKER_URL,
                            configuration[CONFIGURATION].MQTT_BROKER_PORT)

        # Register callback functions to each topic
        self.client.message_callback_add('baby_monitor_project/register/monitor', baby_monitor_project_register_monitor)
        self.client.message_callback_add('baby_monitor_project/update/monitor', baby_monitor_project_update_monitor)
        self.client.message_callback_add('baby_monitor_project/data/monitor', baby_monitor_project_data_monitor)

        self.client.loop_start()

    def start(self):
        self.mqtt_thread = threading.Thread(target=self.start_mqtt_thread)
        self.mqtt_thread.start()

    def stop(self):
        self.client.loop_stop()