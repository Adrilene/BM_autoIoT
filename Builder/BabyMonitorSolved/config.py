import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Application Name
PRODUCT_NAME = 'AutoIoT.{}'.format('')

class Config:
    WTF_CSRF_ENABLED = True
    SECRET_KEY = 'asdf1234' # HINT: Choose a better SECRET_KEY

    STATIC_FOLDER = 'static' # Static folder path

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #MQTT Broker Configuration
    MQTT_BROKER_URL = 'localhost'
    MQTT_BROKER_PORT = 1883
    MQTT_USERNAME = 'admin'
    MQTT_PASSWORD = 'public'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    # Database Configuration
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

    # Advanced Database Configuration
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository') # Directory to help migrate database schema

configuration = {
    'development': DevelopmentConfig
}