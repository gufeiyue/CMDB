# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import render_template, request, redirect, url_for, flash, jsonify
from . import asset
from ..models import All_hosts, Status, Cmdb_env
from .forms import QueryForm, EditHostInfoForm
from flask_login import login_required
from .. import db
from flask import json


@asset.route('/manage_hosts', methods=['GET', 'POST'])
@login_required
def manage_hosts():
    env_id = request.args.get('env_id', -1, type=str)
    used_id = request.args.get('used_id', -1, type=str)
    password_id = request.args.get('password_id', -1, type=str)
    ip = request.args.get('ip', '', type=str)

    form = QueryForm(request.form, env=env_id, used=used_id, password_id=password_id, ip=ip)
    form2 = EditHostInfoForm()

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    envs.append(("-1", u'全部环境'))

    use_status = [("-1", u'IP状态'), ('Y', u'IP已使用'), ('N', u'IP未占用')]

    password_verify = [("-1", u'密码状态'), ('error', u'错误'), ('correct', u'正确')]

    form.env.choices = envs
    form.used.choices = use_status
    form.verify.choices = password_verify
    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('password_id') is not None and request.args.get('used_id') is not None and request.args.get('env_id') is not None):
        if form.validate_on_submit():
            env_id = form.env.data
            used_id = form.used.data
            password_id = form.verify.data
            ip = form.ip.data
            page = 1
        else:
            env_id = request.args.get('env_id')
            used_id = request.args.get('used_id')
            password_id = request.args.get('password_id')
            form.env.data = env_id
            form.used.data = used_id
            form.verify.data = password_id
            ip = form.ip.data
            page = request.args.get('page', 1, type=int)

        hosts_list = All_hosts.query.order_by(All_hosts.ip)

        if env_id != "-1" and env_id is not None:
            hosts_list = hosts_list.filter_by(env=env_id)
        if used_id != "-1" and used_id is not None:
            hosts_list = hosts_list.filter_by(is_used=used_id)
        if password_id != "-1" and password_id is not None:
            hosts_list = hosts_list.filter_by(passwd_result=password_id)
        if ip != '' and ip is not None:
            ipp = "%" + ip + "%"
            #hosts_list = hosts_list.filter(All_hosts.ip.like(ipp))

            hosts_list = hosts_list.filter(All_hosts.ip.like(ipp) | All_hosts.hostname.like(ipp))

        pagination_search = hosts_list.paginate(page, per_page=20, error_out=False)
    if pagination_search != 0:
        pagination = pagination_search
        hosts_list = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = All_hosts.query.order_by(All_hosts.ip).paginate(
                page, per_page=20,
                error_out=True)
        hosts_list = pagination.items

    return render_template('asset/all_cu_lists.html', page=page, hosts_list=hosts_list, env_id=env_id, used_id=used_id, password_id=password_id, ip=ip, form=form, form2=form2, pagination=pagination)


@asset.route('/manage-hosts/get-host-info/<int:id>', methods=['GET', 'POST'])
@login_required
def get_host_info(id):
    print type(id)
    if request.is_xhr:
        host_info = All_hosts.query.get_or_404(id)
        return jsonify({
            'hostname': host_info.hostname,
            'ip': host_info.ip,
            'username': host_info.username,
            'password': host_info.password
        })


@asset.route('/manage_hosts/edit-host-info', methods=['GET', 'POST'])
@login_required
def edit_host_info():
    form2 = EditHostInfoForm()
    ip = form2.ip.data
    username = form2.username.data
    password = form2.password.data
    hostname = form2.hostname.data

    host = All_hosts.query.filter_by(ip=ip).first()

    host.username = username
    host.password = password
    host.hostname = hostname
    db.session.commit()
    flash(u'修改host信息成功！', 'success')
    return redirect(url_for('asset.manage_hosts'))





