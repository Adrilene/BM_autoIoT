import paho.mqtt.client as mqtt
import threading
import json

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
    {% for topic in project.get_mqtt_protocol().topics %}
    client.subscribe('{{topic.topic}}')
    {% endfor %}

{% for topic in project.get_mqtt_protocol().topics %}
def {{topic.get_function_name()}}(client, userdata, msg):
    '''
    Callback function triggered when a message arrives in the topic "{{topic.topic}}"
    '''
{% for line in topic.code.split('\n') %}
    {{line}}
    {{'TESTE'}}
{% endfor %}
{% endfor %}

#MQTT Manager class responsible for the communication between application and MQTT Broker.
class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client(client_id='{{project.name}}.{{time_now()}}')

    def start_mqtt_thread(self):
        self.client.on_connect = on_connect

        if (configuration[CONFIGURATION].MQTT_USERNAME != '' and configuration[
            CONFIGURATION].MQTT_PASSWORD != ''):
            self.client.username_pw_set(configuration[CONFIGURATION].MQTT_USERNAME,
                                        password=configuration[CONFIGURATION].MQTT_PASSWORD)

        self.client.connect(configuration[CONFIGURATION].MQTT_BROKER_URL,
                            configuration[CONFIGURATION].MQTT_BROKER_PORT)

        # Register callback functions to each topic
        {% for topic in project.get_mqtt_protocol().topics %}
        self.client.message_callback_add('{{topic.topic}}', {{topic.get_function_name()}})
        {% endfor %}

        self.client.loop_start()

    def start(self):
        self.mqtt_thread = threading.Thread(target=self.start_mqtt_thread)
        self.mqtt_thread.start()

    def stop(self):
        self.client.loop_stop()