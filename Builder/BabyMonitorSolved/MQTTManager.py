import paho.mqtt.client as mqtt
import threading
import json
import random

from models import *

from config import configuration

CONFIGURATION = 'development'

#Globals

# -Variables useful to change data
maxNoChangesB = random.randint(8,15) 
maxNoChangesC = random.randint(8,15) 
breathing = random.choices([False, True], [0.75, 0.25], k = 1)[0]
crying = random.choices([True, False], [0.2, 0.8], k = 1)[0]
flag = -1
changesB = 0 
changesC = 0
tv = None
notification = None
lock = threading.Lock()
lock2 = threading.Lock()

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
    client.subscribe('baby_monitor_project/register/smart_phone')
    client.subscribe('baby_monitor_project/update/smart_phone')
    client.subscribe('baby_monitor_project/data/smart_phone')
    client.subscribe('baby_monitor_project/register/smart_tv')
    client.subscribe('baby_monitor_project/update/smart_tv')
    client.subscribe('baby_monitor_project/data/smart_tv')

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
    
            
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'name' in message:
                device.name = message['name']
            
            if 'key' in message:
                device.key = message['key']
            
    
            db.session.add(device)
            db.session.commit()
    
            device.init_sensors()
        else:
            #print('Device already in the database.')
            pass
    
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
    
            
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'name' in message:
                device.name = message['name']
            
            if 'key' in message:
                device.key = message['key']
            
    
            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database

            print('Device not in the database.')
    
    except Exception as e:
        print(e)

#It makes the change of the baby's breathing status
def chooseBreathing(crying, flag):
    global maxNoChangesB, breathing, changesB

    if flag == True or crying == True:
        breathing = True
        changesB = 0 
    
    elif changesB >= maxNoChangesB: 
        random.seed()
        maxNoChangesB = random.randint(5,15)
        changesB = 0
        breathing = random.choices([False, True], [0.75, 0.25], k = 1)[0]  
    else: 
        changesB += 2   

def chooseCrying(flag):
    global maxNoChangesC, changesC, crying
    
    if flag == -1:
        
        if changesC >= maxNoChangesC: 
            random.seed()
            crying = random.choices([True, False], [0.2,0.8], k = 1)[0]
            maxNoChangesC = random.randint(8,15)
            changesC = 0
        else:
            changesC += 1

    elif flag == 1: 
        crying = False
        changesC = 0
    
    elif flag == 0: 
        print("Couldn't reach SmartPhone.")
        changesC += 1


def baby_monitor_project_data_monitor(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/data/monitor"
    '''
    global tv, lock
    try:
        global breathing, changesB, notification
        message = json.loads(msg.payload)
        device = Monitor.query.filter_by(key=message['key']).first()
        smP = SmartPhone.query.filter_by(key=message['key']).first()

        if device: #Device in the database
            #print('Adding data to device.')  
            if 'crying_sensor_sensor' in message:
                global flag, crying

                chooseCrying(flag)
                message['crying_sensor_sensor']['crying'] = crying

                device.crying_sensor_sensor.add_metric_from_dict(message['crying_sensor_sensor'])

                if message['crying_sensor_sensor']['crying']: 
                    print('Alert parents!')
                    notification = 'The baby is crying!'
                    flag = chooseCrying(smP.notification_sensor_sensor.add_metric(notification))
                else:
                    flag = -1

            if 'sleeping_sensor_sensor' in message:
                random.seed()
                message['sleeping_sensor_sensor']['sleeping'] = random.choices([True, False], [0.8, 0.20], k = 1)[0]
                
                if message['crying_sensor_sensor']['crying']: 
                    message['sleeping_sensor_sensor']['sleeping'] = False

                device.sleeping_sensor_sensor.add_metric_from_dict(message['sleeping_sensor_sensor'])

            if 'breathing_sensor_sensor' in message:
                
                chooseBreathing(message['crying_sensor_sensor']['crying'], 0)
                message['breathing_sensor_sensor']['breathing'] = breathing

                if not breathing:
                    message['breathing_sensor_sensor']['time_no_breathing'] = changesB
                
                else:
                    message['breathing_sensor_sensor']['time_no_breathing'] = 0 
                
                if message['breathing_sensor_sensor']['time_no_breathing'] > 5:
                    print('Alert parents!')
                    notification = "The baby hasn't been breathing for {} seconds!".format(changesB)
                    lock.acquire()
                    if not smP.notification_sensor_sensor.add_metric(notification): 
                        print('No answer from smartphone.')
                        print('Trying to reach TV...')
                        if send_message_smarttv(smP):
                            chooseBreathing(message['crying_sensor_sensor']['crying'], 1)
                        lock.release()
                    else: 
                        chooseBreathing(message['crying_sensor_sensor']['crying'],1)
                        lock.release()
                baby_monitor_project_data_smart_phone(client, userdata, msg)
                device.breathing_sensor_sensor.add_metric_from_dict(message['breathing_sensor_sensor'])

            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database
            #print('Device monitor not in the database. ', device)
            baby_monitor_project_register_monitor(client, userdata, msg)
    
    except Exception as e:
        print(e)

def baby_monitor_project_register_smart_phone(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/register/smart_phone"
    '''
    try:
        message = json.loads(msg.payload)
        device = SmartPhone.query.filter_by(key=message['key']).first()
    
        if not device: #Device is not in the database
            print('Creating new device.')
            device = SmartPhone()
            device.key = message['key']
    
            
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'name' in message:
                device.name = message['name']
            
            if 'key' in message:
                device.key = message['key']
                
            db.session.add(device)
            db.session.commit()
    
            device.init_sensors()
        else:
            #print('Device already in the database.')
            pass
    
    except Exception as e:
        print(e)
            
def baby_monitor_project_update_smart_phone(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/update/smart_phone"
    '''
    try:
        message = json.loads(msg.payload)
        device = SmartPhone.query.filter_by(key=message['key']).first()
    
        if device: #Device in the database
            print('Updating device.')
            
            device.key = message['key']
    
            
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'name' in message:
                device.name = message['name']
            
            if 'key' in message:
                device.key = message['key']
            
    
            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database
            print('Device not in the database.')
    
    except Exception as e:
        print(e)
            
def baby_monitor_project_data_smart_phone(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/data/smart_phone"
    '''
    try:
        message = json.loads(msg.payload)
        device = SmartPhone.query.filter_by(key=message['key']).first()
        monitor = Monitor.query.filter_by(key=message['key']).first()
        
        if device: #Device in the database
            
            if 'notification_sensor_sensor' in message:

                baby_monitor_project_register_smart_phone(client, userdata, msg)
                device.notification_sensor_sensor.add_metric_from_dict(message['notification_sensor_sensor']) 

            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database
            #print('Device not in the database.')
            baby_monitor_project_register_smart_phone(client, userdata, msg)
           
    except Exception as e:
        print(e)

def send_message_smarttv(smP):
    global tv, notification, lock
   
    if tv:
        sensorTv = tv.command_sensor_sensor.get_last_metric_data('status')

        if not getattr(sensorTv, 'status'):
            
            if not tv.command_sensor_sensor.add_metric("status true", smP):
                print('Error connecting the TV')
                return False
            print('STATUS: ', getattr(sensorTv, 'status'))   

        if getattr(sensorTv, 'status') and tv.command_sensor_sensor.add_metric(str("message " + notification), smP):
            lock2.acquire()
            tv.command_sensor_sensor.add_metric("status false", smP)
            lock2.release()
            return True
        else:
            print('Error sending the message to TV.')
            return False
    else:
        print('TV is off')
        return False

def baby_monitor_project_register_smart_tv(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/register/smart_tv"
    '''
    global tv
    
    try:
        message = json.loads(msg.payload)
        device = SmartTv.query.filter_by(key=message['key']).first()
        
        if not device: #Device is not in the database
            print('Creating new device.')
            device = SmartTv(False)
            device.key = message['key']
                        
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'name' in message:
                device.name = message['name']
            
            if 'key' in message:
                device.key = message['key']

            tv = device
    
            db.session.add(device)
            db.session.commit()
    
            device.init_sensors()
        else:
            #print('Device already in the database.')
            pass
    
    except Exception as e:
        print(e)
            
def baby_monitor_project_update_smart_tv(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/update/smart_tv"
    '''
    
    try:
        message = json.loads(msg.payload)
        device = SmartTv.query.filter_by(key=message['key']).first()
    
        if device: #Device in the database
            print('Updating device.')
            
            device.key = message['key']
    
            if 'barcode' in message:
                device.barcode = message['barcode']
            
            if 'name' in message:
                device.name = message['name']
            
            if 'key' in message:
                device.key = message['key']
            
    
            db.session.add(device)
            db.session.commit()
    
        else: #Device not in the database
            print('Device not in the database.')
    
    except Exception as e:
        print(e)
            
def baby_monitor_project_data_smart_tv(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "baby_monitor_project/data/smart_tv"
    '''
    global changesB, tv
    
    try:
        message = json.loads(msg.payload)
        device = SmartTv.query.filter_by(key=message['key']).first()
        
        if not tv:
            tv = device
            tv.command_sensor_sensor.change_status(random.choice([True, False]))

        if device: #Device in the database
            #print('Adding data to device TV.')                
            #tv = device
            if 'command_sensor_sensor' in message:
                device.command_sensor_sensor.add_metric_from_dict(message['command_sensor_sensor'])
            db.session.add(device)
            db.session.commit()

        else: #Device not in the database
            #print('Device SmartTV not in the database.')
            baby_monitor_project_register_smart_tv(client, userdata, msg)            

    except Exception as e:
        print(e)

#MQTT Manager class responsible for the communication between application and MQTT Broker.
class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client(client_id='Baby Monitor Project.1579018467.080065')

    def start_mqtt_thread(self):
        self.client.on_connect = on_connect

        if (configuration[CONFIGURATION].MQTT_USERNAME != '' and configuration[
            CONFIGURATION].MQTT_PASSWORD != ''):
            self.client.username_pw_set(configuration[CONFIGURATION].MQTT_USERNAME,
                                        password=configuration[CONFIGURATION].MQTT_PASSWORD)

        self.client.connect(configuration[CONFIGURATION].MQTT_BROKER_URL,
                            configuration[CONFIGURATION].MQTT_BROKER_PORT)

        # Register callback functions to each topic
        
        #### SmartTV ####
        self.client.message_callback_add('baby_monitor_project/register/smart_tv', baby_monitor_project_register_smart_tv)
        self.client.message_callback_add('baby_monitor_project/update/smart_tv', baby_monitor_project_update_smart_tv)
        self.client.message_callback_add('baby_monitor_project/data/smart_tv', baby_monitor_project_data_smart_tv)
        
        #### Monitor ####
        self.client.message_callback_add('baby_monitor_project/register/monitor', baby_monitor_project_register_monitor)
        self.client.message_callback_add('baby_monitor_project/update/monitor', baby_monitor_project_update_monitor)
        self.client.message_callback_add('baby_monitor_project/data/monitor', baby_monitor_project_data_monitor)
        
        #### SmartPhone ####
        self.client.message_callback_add('baby_monitor_project/register/monitor', baby_monitor_project_register_smart_phone)
        self.client.message_callback_add('baby_monitor_project/update/monitor', baby_monitor_project_update_smart_phone)
        #self.client.message_callback_add('baby_monitor_project/data/monitor', baby_monitor_project_data_smart_phone)
    

        self.client.loop_start()

    def start(self):
        self.mqtt_thread = threading.Thread(target=self.start_mqtt_thread)
        self.mqtt_thread.start()

    def stop(self):
        self.client.loop_stop()