# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import render_template, request, redirect, url_for, flash, jsonify
from . import admin
from ..models import All_hosts, Env, Status
from .forms import QueryForm, EditHostInfoForm
from flask_login import login_required
from .. import db
from flask import json



@admin.route('/', methods=['GET', 'POST'])
@login_required
def index():
    used_count = All_hosts.query.filter_by(is_used="Y").count()
    passwd_count = All_hosts.query.filter_by(passwd_result="error").count()
    return render_template('admin/dash.html', used_count=used_count, passwd_count=passwd_count)







