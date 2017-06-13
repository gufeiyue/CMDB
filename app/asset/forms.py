# coding:utf-8

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField, \
    PasswordField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo



class QueryForm(FlaskForm):
    env = SelectField(u'全部环境', coerce=str)
    used = SelectField(u'是否使用', coerce=str)
    verify = SelectField(u'password', coerce=str)
    ip = StringField(u'ip')


class EditHostInfoForm(QueryForm):
    username = StringField(u'用户名', validators=[DataRequired()])
    password = StringField(u'密码', validators=[DataRequired()])
    hostname = StringField(u'HOSTNAME', validators=[DataRequired()])

