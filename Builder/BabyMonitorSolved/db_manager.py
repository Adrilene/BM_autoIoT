from flask_script import Manager
from flask_migrate import MigrateCommand
from main import app
import os
import subprocess

from models.User import User

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def init():
    print('Creating admin user and inserting roles in the database')
    User.init()

@manager.command
def geoalchemy():
    files = os.listdir(os.path.join('migrations', 'versions'))

    for f in files:
        if os.path.isfile(os.path.join('migrations', 'versions', f)):
            already_imported = False
            content = ''
            with open(os.path.join('migrations', 'versions', f), 'r') as file:
                content = file.read()

            # Check if already have already_imported
            for line in content.split('\n'):
                if 'import geoalchemy2' in line:
                    already_imported = True
                    break

            if not already_imported:
                with open(os.path.join('migrations', 'versions', f), 'w+') as file:
                    file.write('import geoalchemy2\n' + content)



#Exclude table spatial_ref_sys from migrations
@manager.command
def fix():
    already_changed = False
    content = ''
    with open(os.path.join('migrations', 'alembic.ini'), 'r') as file:
        content = file.read()

        # Check if already have [alembic:exclude]
        for line in content.split('\n'):
            if '[alembic:exclude]' in line:
                already_changed = True

    #Change all loggers to WARN
    content_copy = content
    content = ''
    for line in content_copy.split('\n'):
        if 'level = INFO' in line:
            content += 'level = WARN' + '\n'
        else:
            content += line + '\n'

    if not already_changed:
        with open(os.path.join('migrations', 'alembic.ini'), 'w+') as file:
            file.write(content + '\n[alembic:exclude]\ntables = spatial_ref_sys\n')
    else:
        with open(os.path.join('migrations', 'alembic.ini'), 'w+') as file:
            file.write(content)

    with open(os.path.join('migrations', 'env.py'), 'w+') as file:
        file.write("""
from __future__ import with_statement
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import logging

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from flask import current_app
config.set_main_option('sqlalchemy.url',
                       current_app.config.get('SQLALCHEMY_DATABASE_URI'))
target_metadata = current_app.extensions['migrate'].db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def exclude_tables_from_config(config_):
    tables_ = config_.get("tables", None)
    if tables_ is not None:        
        tables = tables_.split(",")

    print(tables)
    return tables

exclude_tables = exclude_tables_from_config(config.get_section('alembic:exclude'))


def include_object(object, name, type_, reflected, compare_to):    
    if type_ == "table" and name in exclude_tables:
        return False
    else:
        return True

def run_migrations_offline():

    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, include_object=include_object)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    engine = engine_from_config(config.get_section(config.config_ini_section),
                                prefix='sqlalchemy.',
                                poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(connection=connection,
                      target_metadata=target_metadata,
                      include_object=include_object,
                      process_revision_directives=process_revision_directives,
                      **current_app.extensions['migrate'].configure_args)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
""")

@manager.command
def setup():
    #INIT
    print('Creating migrations folder...')
    cmd = 'python {} db init'.format(__file__)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()

    if 'Directory migrations already exists' in str(error):
        print('  Directory migrations already exists.')
    elif error != b'':
        print('--------------------ERROR--------------------')
        print(error)

    #FIX
    print('Changing alembic.ini to ignore spatial_ref_sys table...')
    cmd = 'python {} fix'.format(__file__)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()

    if error != b'':
        print('--------------------ERROR--------------------')
        print(error)

    #MIGRATE
    print('Creating migration file...')
    cmd = 'python {} db migrate'.format(__file__)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()


    if 'No changes in schema detected' in str(error):
        print('  No changes in schema detected.')
    elif error != b'':
        print('--------------------ERROR--------------------')
        print(error)

    #UPDATE
    print('Fix migrations to import geoalchemy2...')
    cmd = 'python {} geoalchemy'.format(__file__)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()

    if error != b'':
        print('--------------------ERROR--------------------')
        print(error)

    #UPDATE
    print('Updating database...')
    cmd = 'python {} db upgrade'.format(__file__)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()

    if error != b'':
        print('--------------------ERROR--------------------')
        print(error)

    #USERS
    print('Inserting users in the database...')
    cmd = 'python {} init'.format(__file__)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, error = p.communicate()

    if error != b'':
        print('--------------------ERROR--------------------')
        print(error)

#Import models
from models.Monitor import Monitor

from models.MonitorBreathingSensor import MonitorBreathingSensor

from models.MonitorBreathingSensorData import MonitorBreathingSensorData

from models.MonitorSleepingSensor import MonitorSleepingSensor

from models.MonitorSleepingSensorData import MonitorSleepingSensorData

from models.MonitorCryingSensor import MonitorCryingSensor

from models.MonitorCryingSensorData import MonitorCryingSensorData


from models.SmartPhone import SmartPhone

from models.SmartPhoneNotificationSensor import SmartPhoneNotificationSensor

from models.SmartPhoneNotificationSensorData import SmartPhoneNotificationSensorData


from models.SmartTv import SmartTv

from models.SmartTvCommandSensor import SmartTvCommandSensor

from models.SmartTvCommandSensorData import SmartTvCommandSensorData



if __name__ == '__main__':
    manager.run()