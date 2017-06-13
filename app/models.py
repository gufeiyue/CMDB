#coding: utf-8

from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for




# class User(UserMixin, db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(64), unique=True, index=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     password_hash = db.Column(db.String(128))

class Auth_user(UserMixin, db.Model):
    __tablename__ = 'auth_user'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(128), unique=True, index=True)
    last_login = db.Column(db.DateTime)
    is_superuser = db.Column(db.Integer)
    username = db.Column(db.String(128))
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(254))
    is_staff = db.Column(db.Integer)
    is_active = db.Column(db.Integer)
    date_joined = db.Column(db.DateTime)

    # @property
    # def passwords(self):
    #     raise AttributeError('passwords is not a readable attribute')
    #
    # @passwords.setter
    # def passwords(self, passwords):
    #     self.password = generate_password_hash(passwords)
    #
    # def verify_password(self, passwords):
    #     return check_password_hash(self.password, passwords)
    #
    # def generate_confirmation_token(self, expiration=3600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expiration)
    #     return s.dumps({'confirm': self.id})


@login_manager.user_loader
def load_user(user_id):
    return Auth_user.query.get(int(user_id))



class All_hosts(db.Model):
    __tablename__ = 'all_hosts'
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64))
    ip = db.Column(db.String(16))
    username = db.Column(db.String(16))
    password = db.Column(db.String(16))
    systeminfo = db.Column(db.String(64))
    env = db.Column(db.Integer)
    is_used = db.Column(db.Integer)
    passwd_result = db.Column(db.Integer)
    description = db.Column(db.String(128))

    def __init__(self, id, hostname, ip, username, password, systeminfo, env, is_used, passwd_result, description):
        self.id = id
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
        self.systeminfo = systeminfo
        self.env = env
        self.is_used = is_used
        self.passwd_result = passwd_result
        self.description = description

    def __repr__(self):
        return self.ip



class Env(db.Model):
    __tablename__ = 'env'
    id = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(64))

    def __init__(self, id, env):
        self.id = id
        self.env = env

    def __repr__(self):
        return self.env


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(64))

    def __init__(self, id, description):
        self.id = id
        self.description = description

    def __repr__(self):
        return self.description







class Cmdb_env(db.Model):
    __tablename__ = 'cmdb_env'
    id = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(32))
    version = db.Column(db.String(32))
    type = db.Column(db.String(32))
    update_time = db.Column(db.DateTime)
    description = db.Column(db.String(256))


class Cmdb_system(db.Model):
    __tablename__ = 'cmdb_system'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    conf_git_url = db.Column(db.String(300))
    flag = db.Column(db.String(2))
    parent_id = db.Column(db.String(1))
    description = db.Column(db.String(32))


class Cmdb_conf_file(db.Model):
    __tablename__ = 'cmdb_conf_file'
    id = db.Column(db.Integer, primary_key=True)
    conf_file = db.Column(db.String(256))
    status = db.Column(db.String(32))
    description = db.Column(db.String(256))


class Cmdb_conf_key(db.Model):
    __tablename__ = 'cmdb_conf_key'
    id = db.Column(db.Integer, primary_key=True)
    sub_system = db.Column(db.String(32))
    conf_file = db.Column(db.String(256))
    conf_key = db.Column(db.String(256))
    branch_name = db.Column(db.String(32), default='')
    jira_id = db.Column(db.String(32), default='')
    status = db.Column(db.String(32))
    description = db.Column(db.String(256))


class Cmdb_conf_key_value(db.Model):
    __tablename__ = 'cmdb_conf_key_value'
    id = db.Column(db.Integer, primary_key=True)
    conf_env = db.Column(db.String(32))
    conf_key_id = db.Column(db.Integer, db.ForeignKey('cmdb_conf_key.id'))
    conf_value = db.Column(db.String(300), default='')
    description = db.Column(db.String(256))


class Cmdb_conf_special_key_value(db.Model):
    __tablename__ = 'cmdb_conf_special_key_value'
    id = db.Column(db.Integer, primary_key=True)
    conf_env = db.Column(db.String(32))
    conf_key_id = db.Column(db.Integer, db.ForeignKey('cmdb_conf_special_key.id'))
    conf_value = db.Column(db.String(300), default='')
    description = db.Column(db.String(256))



class Cmdb_conf_special_key(db.Model):
    __tablename__ = 'cmdb_conf_special_key'
    id = db.Column(db.Integer, primary_key=True)
    sub_system = db.Column(db.String(32))
    conf_file = db.Column(db.String(256))
    conf_key = db.Column(db.String(256))
    branch_name = db.Column(db.String(32), default='')
    jira_id = db.Column(db.String(32), default='')
    status = db.Column(db.String(32))
    description = db.Column(db.String(256))
    values = db.relationship('Cmdb_conf_special_key_value',backref='cmdb_conf_special_key', lazy='dynamic')


#posts = db.relationship('Post', backref='author', lazy='dynamic')


class Conf_key_value1(db.Model):
    __tablename__ = 'conf_key_value1'
    id = db.Column(db.Integer, primary_key=True)
    conf_env = db.Column(db.String(32))
    sub_system = db.Column(db.String(32))
    conf_file = db.Column(db.String(256))
    conf_key = db.Column(db.String(256))
    conf_value = db.Column(db.String(300))
    version = db.Column(db.String(32))
    status = db.Column(db.String(32))
    description = db.Column(db.String(256))


class Cmdb_conf_version(db.Model):
    __tablename__ = 'cmdb_conf_version'
    id = db.Column(db.Integer, primary_key=True)
    env = db.Column(db.String(32))
    conf_version = db.Column(db.String(256))
    update_time = db.Column(db.DateTime)
    description = db.Column(db.String(256))


class Cmdb_other_config(db.Model):
    __tablename__ = 'cmdb_other_config'
    id = db.Column(db.Integer, primary_key=True)
    iterm = db.Column(db.String(32))
    value = db.Column(db.String(256))


class Req_manage(db.Model):
    __tablename__ = 'req_manage'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(32))
    jira_id = db.Column(db.String(32))
    jira_title = db.Column(db.String(32))
    req_type = db.Column(db.String(32))
    branch_name = db.Column(db.String(32))
    project_manager = db.Column(db.String(32))
    dev = db.Column(db.String(32))
    test = db.Column(db.String(32))
    expected_time = db.Column(db.String(32))
    actul_time = db.Column(db.String(32))
    status = db.Column(db.String(32))
    sql = db.Column(db.String(32))
    remark = db.Column(db.String(32))


class Superlight_config(db.Model):
    __tablename__ = 'superlight_config'
    id = db.Column(db.Integer, primary_key=True)
    jira_id = db.Column(db.String(32))
    branch_name = db.Column(db.String(300))
    sub_system = db.Column(db.String(32))
    file_name = db.Column(db.String(32))
    key = db.Column(db.String(32))
    value = db.Column(db.String(300))
    env_name = db.Column(db.String(32))
    operation = db.Column(db.String(32))

