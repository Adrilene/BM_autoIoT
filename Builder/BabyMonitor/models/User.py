from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from main import app, db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


    def get_created_date(self):
        return self.created_at.strftime("%d/%m/%Y")

    def getLastActivity(self):
        return self.last_seen.strftime("%d/%m/%y")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User {} - {}>'.format(self.username, self.role)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    #Check if the user can perform a specif action
    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    # Check if the user have administrator rights
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    # Check if the user have administrator rights
    def is_moderator(self):
        return self.can(Permission.MANAGE_COURSES)

    @staticmethod
    def init():
        Role.insert_roles()

        role = Role.query.filter_by(name='Administrator').first()

        quant_users = User.query.count()

        if quant_users == 0:
            user = User(username='admin', email='admin.user@autoiot.de', role=role)
            user.password = 'admin'

            db.session.add(user)
            db.session.commit()


#Pag 112 from Flask Web Development
#Change ACTIONS to match proper actions later
class Permission:
    ACTION_1 = 0x01
    ACTION_2 = 0x02
    ACTION_3 = 0x04
    ACTION_4 = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Integer, default=0, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "<Role {}>".format(self.name)

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.ACTION_1 |
                     Permission.ACTION_2 |
                     Permission.ACTION_3, 1),
            'Moderator': (Permission.ACTION_1 |
                          Permission.ACTION_2 |
                          Permission.ACTION_3 |
                          Permission.ACTION_4, 0),
            'Administrator': (0xff, 0)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()