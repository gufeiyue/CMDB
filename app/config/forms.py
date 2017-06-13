# coding:utf-8

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, SubmitField, \
    PasswordField, SelectMultipleField, FieldList
from wtforms.validators import DataRequired, Length, Email, EqualTo




class AddEnvForm(FlaskForm):
    envs = StringField(u'环境', validators=[DataRequired()])
    description = TextAreaField(u'环境说明')


class AddEnvItermForm(AddEnvForm):
    env_iterm_template = SelectField(u'配置项模板', validators=[DataRequired()])


class AddSubSystemForm(FlaskForm):
    systems = StringField(u'子系统', validators=[DataRequired()])
    description = TextAreaField(u'环境说明')


class AddFileForm(FlaskForm):
    conf_file = StringField(u'文件名', validators=[DataRequired()])
    description = TextAreaField(u'环境说明')


class AddKeyForm(FlaskForm):
    systems = SelectField(u'子系统', validators=[DataRequired()])
    files = SelectField(u'文件名', validators=[DataRequired()])
    keys = TextAreaField(u'key', validators=[DataRequired()])
    branch_name = StringField(u'branch_name', validators=[DataRequired()])
    jira_id = StringField(u'jira_id', validators=[DataRequired()])
    description = TextAreaField(u'配置项说明')


class QueryKeyForm(FlaskForm):
    systems = SelectField(u'子系统')
    files = SelectField(u'文件名')
    keys = StringField(u'keys')



class CheckKeyForm(FlaskForm):
    systems = SelectField(u'子系统', validators=[DataRequired()])
    path = TextAreaField(u'路径', validators=[DataRequired()])


class AddKeyValueForm(FlaskForm):
    envs = SelectField(u'环境', validators=[DataRequired()])
    systems = SelectField(u'子系统', validators=[DataRequired()])
    files = SelectField(u'文件名', validators=[DataRequired()])
    keys = TextAreaField(u'key', validators=[DataRequired()])
    values = TextAreaField(u'value', validators=[DataRequired()])
    jira_id = StringField(u'jira_id')
    branch_name = StringField(u'branch_name')
    description = TextAreaField(u'配置项说明')


class EditKeyValueForm(FlaskForm):
    envs = SelectField(u'环境', validators=[DataRequired()])
    systems = SelectField(u'子系统')
    files = SelectField(u'文件名')
    keys = TextAreaField(u'key')
    values = TextAreaField(u'value', validators=[DataRequired()])
    version = StringField(u'version')
    description = TextAreaField(u'配置项说明')


class BatchAddKeyValueForm(FlaskForm):
    systems = SelectField(u'子系统', validators=[DataRequired()])
    files = SelectField(u'文件名', validators=[DataRequired()])
    keys = TextAreaField(u'key', validators=[DataRequired()])
    jira_id = StringField(u'jira_id')
    branch_name = StringField(u'branch_name', validators=[DataRequired()])
    description = TextAreaField(u'环境说明')


class BatchEditKeyValueForm(FlaskForm):
    systems = SelectField(u'子系统', validators=[DataRequired()])
    files = SelectField(u'文件名', validators=[DataRequired()])
    keys = TextAreaField(u'key', validators=[DataRequired()])
    version = StringField(u'version', validators=[DataRequired()])
    description = TextAreaField(u'环境说明')


class QueryKeyValueForm(FlaskForm):
    envs = SelectField(u'环境')
    systems = SelectField(u'子系统')
    files = SelectField(u'文件名')
    keys = StringField(u'keys')


class QueryFileForm(FlaskForm):
    conf_file = StringField(u'文件名')


class QueryVersionForm(FlaskForm):
    envs = SelectField(u'环境')
    versions = StringField(u'versions')

class AddVersionForm(FlaskForm):
    envs = SelectField(u'环境', validators=[DataRequired()])
    git_branchs = TextAreaField(u'配置项说明')
    description = TextAreaField(u'配置项说明')
