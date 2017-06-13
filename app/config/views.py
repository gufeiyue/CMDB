# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import render_template, request, redirect, url_for, flash, jsonify
from . import config
from ..models import Cmdb_env, Cmdb_conf_file, Cmdb_other_config, Conf_key_value1, Cmdb_system, Cmdb_conf_key, Cmdb_conf_key_value, Cmdb_conf_version, Cmdb_conf_special_key, Cmdb_conf_special_key_value
from .forms import AddEnvForm, AddFileForm, AddKeyValueForm, QueryKeyValueForm, QueryFileForm, AddEnvItermForm, \
    BatchAddKeyValueForm, AddSubSystemForm, CheckKeyForm, AddKeyForm, QueryKeyForm, QueryVersionForm, EditKeyValueForm,\
    AddVersionForm
from flask_login import login_required
from .. import db
import fileinput
import shutil
import os, time, re
import requests
from sqlalchemy import func
import get_tree_json
from sqlalchemy import or_

'''
环境列表
'''

@config.route('/env', methods=['GET', 'POST'])
@login_required
def env():
    env_lists = Cmdb_env.query.order_by(Cmdb_env.id)

    return render_template('config/env_list.html', env_lists=env_lists)


'''
环境新增
'''

@config.route('/env_add', methods=['GET', 'POST'])
@login_required
def env_add():
    form = AddEnvForm()
    if form.validate_on_submit():
        env = form.envs.data
        description = form.description.data
        env_info = Cmdb_env.query.filter_by(env=env).first()
        if env_info:
            flash(u'添加环境失败,该环境已存在。', 'danger')
        else:
            env = Cmdb_env(env=env, description=description)
            db.session.add(env)
            db.session.commit()
            return redirect(url_for('config.env'))

    return render_template('config/env_add.html', form=form)


'''
环境配置项新增
'''

@config.route('/env_iterm_add', methods=['GET', 'POST'])
@login_required
def env_iterm_add():
    form = AddEnvItermForm()
    envs = [(t.env, t.env) for t in Cmdb_env.query.all()]
    form.env_iterm_template.choices = envs
    if form.validate_on_submit():
        new_env = form.envs.data
        env_iterm = form.env_iterm_template.data
        description = form.description.data
        env = Cmdb_env(env=new_env, description=description)
        db.session.add(env)
        db.session.commit()

        print type(new_env), new_env
        print type(env_iterm), env_iterm

        add_iterm_sql = "INSERT into `conf_iterm`(`conf_env`, `conf_file`, `original_value`, `replace_value`, `description`, `status`) SELECT" + " '" + new_env + "'" + ", `conf_file`, `original_value`, '', `description`, `status` FROM `conf_iterm` WHERE `conf_env`=" + "'" + env_iterm + "'" + ";"

        db.session.execute(add_iterm_sql)
        db.session.commit()

        print add_iterm_sql

        return redirect(url_for('config.env'))
    return render_template('config/env_iterm_add.html', form=form)



'''
环境删除
'''

@config.route('/env_del', methods=['GET', 'POST'])
@login_required
def env_del():
    id_json = request.get_json()
    id = id_json['data']
    env = Cmdb_env.query.get_or_404(id)
    db.session.delete(env)
    db.session.commit()

'''
环境修改
'''

@config.route('/env_edit', methods=['GET', 'POST'])
@login_required
def env_edit():
    env_id = request.args.get('env_id')
    #print type(env_id)
    env = Cmdb_env.query.get_or_404(env_id)
    form = AddEnvForm()

    if form.validate_on_submit():
        form = AddEnvForm()
        conf_env = form.envs.data
        env_info = Cmdb_env.query.filter_by(env=conf_env).first()

        if env_info and str(env_info.id) != str(env_id):
            flash(u'修改环境失败,该环境已存在。', 'danger')
        else:
            db.session.query(Cmdb_env).filter_by(id=env_id).update({"env": form.envs.data, "description": form.description.data})
            db.session.commit()
            return redirect(url_for('config.env'))


    form.envs.data = env.env
    form.description.data = env.description

    return render_template('config/env_edit.html', form=form)



'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''




'''
子系统列表
'''

@config.route('/sub_system', methods=['GET', 'POST'])
@login_required
def sub_system():
    sub_system_lists = Cmdb_system.query.filter_by(flag="1").order_by(Cmdb_system.id)

    return render_template('config/sub_system_list.html', sub_system_lists=sub_system_lists)


'''
子系统新增
'''

@config.route('/sub_system_add', methods=['GET', 'POST'])
@login_required
def sub_system_add():
    form = AddSubSystemForm()
    if form.validate_on_submit():
        sub_system = form.systems.data
        description = form.description.data

        sub_system_info = Cmdb_system.query.filter_by(name=sub_system).first()
        if sub_system_info:
            flash(u'添加子系统失败,该子系统已存在。', 'danger')
        else:
            sub_system = Cmdb_system(name=sub_system, description=description, flag="1")
            db.session.add(sub_system)
            db.session.commit()

            return redirect(url_for('config.sub_system'))

    return render_template('config/sub_system_add.html', form=form)


'''
子系统删除
'''

@config.route('/sub_system_del', methods=['GET', 'POST'])
@login_required
def sub_system_del():
    id_json = request.get_json()
    id = id_json['data']
    sub_system = Cmdb_system.query.get_or_404(id)
    db.session.delete(sub_system)
    db.session.commit()


'''
子系统修改
'''

@config.route('/sub_system_edit', methods=['GET', 'POST'])
@login_required
def sub_system_edit():
    sub_system_id = request.args.get('sub_system_id')
    sub_system = Cmdb_system.query.get_or_404(sub_system_id)
    print sub_system
    form = AddSubSystemForm()

    if form.validate_on_submit():
        form = AddSubSystemForm()

        name = form.systems.data
        description = form.description.data

        #print sub_system

        sub_system_info = Cmdb_system.query.filter_by(name=name).first()
        print sub_system_info

        if sub_system_info and str(sub_system_info.id) != str(sub_system_id):
            flash(u'修改子系统失败,%s子系统已存在。' % name, 'danger')
        else:
            db.session.query(Cmdb_system).filter_by(id=sub_system_id).update({"name": name, "description": description})
            db.session.commit()
            return redirect(url_for('config.sub_system'))


    form.systems.data = sub_system.name
    form.description.data = sub_system.description

    return render_template('config/sub_system_edit.html', form=form)



'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''



'''
配置文件列表
'''

@config.route('/conf_file', methods=['GET', 'POST'])
@login_required
def conf_file():
    conf_file = request.args.get('conf_file', '', type=str)
    form = QueryFileForm(request.form, conf_file=conf_file)
    file_lists = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id)

    pagination_search = 0

    if form.validate_on_submit():
        conf_file = form.conf_file.data
        page = 1
    else:
        conf_file = form.conf_file.data
        page = request.args.get('page', 1, type=int)

    file_lists = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id)


    if conf_file != '' and conf_file is not None:
        conf_file_like = "%" + conf_file + "%"
        file_lists = file_lists.filter(Cmdb_conf_file.conf_file.like(conf_file_like))

    pagination_search = file_lists.paginate(page, per_page=15, error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        file_lists = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id).paginate(
                page, per_page=15,
                error_out=True)
        file_lists = pagination.items


    return render_template('config/file_list.html', page=page, file_lists=file_lists, conf_file=conf_file, pagination=pagination, form=form)


'''
配置文件新增
'''

@config.route('/file_add', methods=['GET', 'POST'])
@login_required
def file_add():
    form = AddFileForm()

    if form.validate_on_submit():
        conf_file = form.conf_file.data
        description = form.description.data

        file_info = Cmdb_conf_file.query.filter_by(conf_file=conf_file).first()
        if file_info:
            flash(u'添加文件失败,该文件已存在。', 'danger')
        else:
            file = Cmdb_conf_file(conf_file=conf_file,
                           description=description,
                             )
            db.session.add(file)
            db.session.commit()
            return redirect(url_for('config.conf_file'))

    return render_template('config/file_add.html', form=form)


'''
配置文件删除
'''

@config.route('/file_del', methods=['GET', 'POST'])
@login_required
def file_del():
    id_json = request.get_json()
    id = id_json['data']
    file = Cmdb_conf_file.query.get_or_404(id)
    db.session.delete(file)
    db.session.commit()


'''
配置文件修改
'''

@config.route('/file_edit', methods=['GET', 'POST'])
@login_required
def file_edit():
    file_id = request.args.get('file_id')
    file = Cmdb_conf_file.query.get_or_404(file_id)
    form = AddFileForm()

    if form.validate_on_submit():
        conf_file = form.conf_file.data
        description = form.description.data

        file_info = Cmdb_conf_file.query.filter_by(conf_file=conf_file).first()

        if file_info and str(file_info.id) != str(file_id):
            flash(u'添加文件失败,该文件已存在。', 'danger')
        else:
            db.session.query(Cmdb_conf_file).filter_by(id=file.id).update({"conf_file": conf_file, "description": description})
            db.session.commit()
            return redirect(url_for('config.conf_file'))

    form.conf_file.data = file.conf_file
    form.description.data = file.description

    return render_template('config/file_edit.html', form=form)



'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''


'''
配置项检查
'''

@config.route('/key', methods=['GET', 'POST'])
@login_required
def key():
    system_id = request.args.get('system_id', "all", type=str)
    conf_file = request.args.get('conf_file', 'all', type=str)
    conf_key = request.args.get('conf_key', '', type=str)

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    systems.append(("all", u'全部子系统'))

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    files.append(("all", u'全部文件'))

    form = QueryKeyForm(request.form, systems=system_id, files=conf_file, keys=conf_key)

    form.systems.choices = systems
    form.files.choices = files

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('system_id') or \
                     request.args.get('conf_file') or request.args.get('conf_key') is not None):
        print "1"
        if form.validate_on_submit():
            print "2"
            system_id = form.systems.data
            conf_file = form.files.data
            conf_key = form.keys.data
            page = 1
        else:
            print "3"
            system_id = request.args.get('system_id')
            conf_file = request.args.get('conf_file')
            conf_key = request.args.get('conf_key')
            form.systems.data = system_id
            form.files.data = conf_file
            form.keys.data = conf_key
            page = request.args.get('page', 1, type=int)

        key_lists = Cmdb_conf_key.query.order_by(Cmdb_conf_key.id)


        if system_id != "all" and system_id is not None:
            key_lists = key_lists.filter_by(sub_system=system_id)
        if conf_file != "all" and conf_file is not None:
            key_lists = key_lists.filter_by(conf_file=conf_file)
        if conf_key != '' and conf_key is not None:
            conf_key_like = "%" + conf_key + "%"
            print conf_key
            key_lists = key_lists.filter(Cmdb_conf_key.conf_key.like(conf_key_like) | Cmdb_conf_key.branch_name.like(conf_key_like))
            #print key_lists

        pagination_search = key_lists.paginate(page, per_page=15, error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        key_lists = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Cmdb_conf_key.query.order_by(Cmdb_conf_key.id).paginate(
            page, per_page=15,
            error_out=True)
        key_lists = pagination.items
    #print pagination
    print key_lists

    return render_template('config/key_list.html', page=page, key_lists=key_lists, \
                           system_id=system_id, conf_file=conf_file, conf_key=conf_key, pagination=pagination,
                           form=form)






'''
配置项值新增
'''

@config.route('/key_add', methods=['GET', 'POST'])
@login_required
def key_add():
    form = AddKeyForm()


    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files


    if form.validate_on_submit():
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        jira_id = form.jira_id.data
        branch_name = form.branch_name.data
        description = form.description.data

        check_key_isexsit = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).\
            filter_by(conf_key=conf_key).first()

        if check_key_isexsit is None:
            keys = Cmdb_conf_key(sub_system=sub_system,
                           conf_file=conf_file,
                           conf_key=conf_key,
                           jira_id=jira_id,
                           branch_name=branch_name,
                           description=description)

            db.session.add(keys)
            db.session.commit()

            key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).filter_by(conf_key=conf_key).first()
            conf_key_id = key_infos.id

            conf_envs = Cmdb_env.query.filter_by(type="trunk")
            for conf_env in conf_envs:
                env = conf_env.env
                values = Cmdb_conf_key_value(conf_env=env,conf_key_id=conf_key_id)
                db.session.add(values)
                db.session.commit()
            return redirect(url_for('config.key', systems=sub_system, conf_key=conf_key))
        else:
            flash(u'该key在数据库中已存在,请修改', 'danger')

    return render_template('config/key_add.html', form=form)


'''
配置项删除
'''

@config.route('/key_del', methods=['GET', 'POST'])
@login_required
def key_del():
    id_json = request.get_json()
    id = id_json['data']
    print "===="
    print id
    print "===="
    conf_version = Cmdb_conf_key.query.get_or_404(id)
    db.session.delete(conf_version)
    db.session.commit()



'''
配置项修改
'''

@config.route('/key_edit', methods=['GET', 'POST'])
@login_required
def key_edit():
    key_id = request.args.get('key_id')
    print type(key_id)
    key_infos = Cmdb_conf_key.query.get_or_404(key_id)
    print key_infos.conf_file
    print key_infos.sub_system
    print key_infos.conf_key
    print key_infos.branch_name
    print key_infos.description

    print key_infos.jira_id

    form = AddKeyForm()

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files


    if form.validate_on_submit():
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        branch_name = form.branch_name.data
        jira_id = form.jira_id.data
        description = form.description.data

        check_key_isexsit = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).\
            filter_by(conf_key=conf_key).first()

        print type(check_key_isexsit.id)

        if check_key_isexsit is None or str(check_key_isexsit.id) == str(key_id):

            db.session.query(Cmdb_conf_key).filter_by(id=key_id).update({"sub_system": sub_system, \
                                                                            "conf_file": conf_file, "conf_key": conf_key, \
                                                                            "branch_name": branch_name, "jira_id": jira_id, \
                                                                            "description": description})
            db.session.commit()
            return redirect(url_for('config.key'))
        else:
            flash(u'该key在数据库中已存在,请修改', 'danger')


    form.files.data = key_infos.conf_file
    form.systems.data = key_infos.sub_system
    form.keys.data = key_infos.conf_key
    form.branch_name.data = key_infos.branch_name
    form.jira_id.data = key_infos.jira_id
    form.description.data = key_infos.description

    return render_template('config/key_edit.html', form=form)




'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''

'''
配置项值列表
'''


@config.route('/key_value', methods=['GET', 'POST'])
@login_required
def key_value():
    print "11111"
    env_id = request.args.get('env_id', "all", type=str)
    system_id = request.args.get('system_id', "all", type=str)
    conf_file = request.args.get('conf_file', 'all', type=str)
    conf_key = request.args.get('conf_key', '', type=str)

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    envs.append(("all", u'全部环境'))

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    systems.append(("all", u'全部子系统'))

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    files.append(("all", u'全部文件'))

    form = QueryKeyValueForm(request.form, envs=env_id, systems=system_id, files=conf_file, keys=conf_key)

    form.envs.choices = envs
    form.systems.choices = systems
    form.files.choices = files

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('env_id') or request.args.get('system_id') or \
                     request.args.get('conf_file') or request.args.get('conf_key') is not None):
        print "1"
        if form.validate_on_submit():
            print "2"
            env_id = form.envs.data
            system_id = form.systems.data
            conf_file = form.files.data
            conf_key = form.keys.data
            page = 1
        else:
            print "3"
            env_id = request.args.get('env_id')
            system_id = request.args.get('system_id')
            conf_file = request.args.get('conf_file')
            conf_key = request.args.get('conf_key')
            form.envs.data = env_id
            form.systems.data = system_id
            form.files.data = conf_file
            form.keys.data = conf_key
            page = request.args.get('page', 1, type=int)

        # key_value_lists = Conf_key_value1.query.order_by(Conf_key_value1.id)
        # key_value_lists = Cmdb_conf_key.query.join(Cmdb_conf_key_value).order_by(Cmdb_conf_key_value.id)
        key_value_lists = Cmdb_conf_key_value.query.join(Cmdb_conf_key, Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
            Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
            Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
            Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id)

        if env_id != "all" and env_id is not None:
            key_value_lists = Cmdb_conf_key_value.query.filter_by(conf_env=env_id).join(Cmdb_conf_key,
                                                                                        Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
                Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
                Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
                Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id)
        if system_id != "all" and system_id is not None:
            key_value_lists = key_value_lists.filter_by(sub_system=system_id)
        if conf_file != "all" and conf_file is not None:
            key_value_lists = key_value_lists.filter_by(conf_file=conf_file)
        if conf_key != '' and conf_key is not None:
            conf_key_like = "%" + conf_key + "%"
            key_value_lists = key_value_lists.filter(
                Cmdb_conf_key.conf_key.like(conf_key_like) | Cmdb_conf_key.branch_name.like(conf_key_like))

        pagination_search = key_value_lists.paginate(page, per_page=15, error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        key_value_lists = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)

        pagination = Cmdb_conf_key_value.query.join(Cmdb_conf_key, Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
            Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
            Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
            Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id).paginate(
            page, per_page=15,
            error_out=True)

        key_value_lists = pagination.items

    return render_template('config/key_value_list.html', page=page, key_value_lists=key_value_lists, env_id=env_id, \
                           system_id=system_id, conf_file=conf_file, conf_key=conf_key, pagination=pagination,
                           form=form)


'''
配置项值新增
'''


@config.route('/key_value_add', methods=['GET', 'POST'])
@login_required
def key_value_add():
    form = AddKeyValueForm()

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    form.envs.choices = envs

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files

    if form.validate_on_submit():
        env = form.envs.data
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        conf_value = form.values.data
        branch_name = form.branch_name.data
        description = form.description.data

        key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).filter_by(
            conf_key=conf_key).first()
        if key_infos:
            print "pass"
            pass
        else:
            print "sucess"
            iterm_key = Cmdb_conf_key(sub_system=sub_system,
                                 conf_file=conf_file,
                                 conf_key=conf_key,
                                 jira_id=jira_id,
                                 branch_name=branch_name,
                                 description=description)
            db.session.add(iterm_key)
            db.session.commit()

        key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).filter_by(
            conf_key=conf_key).first()

        conf_key_id = key_infos.id

        iterm_value = Cmdb_conf_key_value(conf_key_id=conf_key_id,
                                     conf_env=env,
                                     conf_value=conf_value,
                                     description=description)

        db.session.add(iterm_value)
        db.session.commit()
        return redirect(url_for('config.key_value', conf_file=conf_file, conf_key=conf_key))

    return render_template('config/key_value_add.html', form=form)


'''
配置项值批量新增
'''


@config.route('/key_value_batch_add', methods=['GET', 'POST'])
@login_required
def key_value_batch_add():
    form = BatchAddKeyValueForm()

    envs = Cmdb_env.query.filter_by(type="trunk")

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files

    if form.validate_on_submit():
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        branch_name = form.branch_name.data
        description = form.description.data

        iterm_key = Cmdb_conf_key(sub_system=sub_system,
                             conf_file=conf_file,
                             conf_key=conf_key,
                             branch_name=branch_name,
                             description=description)
        db.session.add(iterm_key)
        db.session.commit()

        key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).filter_by(
            conf_key=conf_key).first()
        conf_key_id = key_infos.id

        for env_info in envs:
            env = env_info.env
            conf_value = request.form[env]
            iterm_value = Cmdb_conf_key_value(conf_key_id=conf_key_id,
                                         conf_env=conf_env,
                                         conf_value=conf_value,
                                         description=description)

            db.session.add(iterm_value)
            db.session.commit()
        return redirect(url_for('config.key_value', conf_file=conf_file, conf_key=conf_key))
    return render_template('config/key_value_batch_add.html', form=form, envs=envs)


'''
配置项值修改
'''


@config.route('/key_value_edit', methods=['GET', 'POST'])
@login_required
def key_value_edit():
    key_id = request.args.get('key_id')
    print "key_id" + key_id
    key_info = Cmdb_conf_key_value.query.get_or_404(key_id)
    env = key_info.conf_env
    print env
    # conf_key_id = key_info.conf_key_id

    # key_infos = Cmdb_conf_key_value.query.filter_by(id=key_id)

    key_infos = Cmdb_conf_key_value.query.filter_by(id=key_id).join(Cmdb_conf_key,
                                                               Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
        Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
        Cmdb_conf_key_value.description, Cmdb_conf_key.sub_system, Cmdb_conf_key.jira_id, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
        Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id).first()

    print key_infos

    form = AddKeyValueForm()

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    form.envs.choices = envs

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files

    print "=====11111===="

    if form.validate_on_submit():
        #env = form.envs.data
        conf_value = form.values.data
        description = form.description.data
        print "=====3333===="


        db.session.query(Cmdb_conf_key_value).filter_by(id=key_id).update({"conf_value": conf_value, \
                                                                      "description": description})
        print "=123-123=123-123"
        db.session.commit()
        return redirect(url_for('config.key_value', sub_system=key_infos.sub_system, conf_key=key_infos.conf_key))

    form.envs.data = key_infos.conf_env
    form.files.data = key_infos.conf_file
    form.systems.data = key_infos.sub_system
    form.keys.data = key_infos.conf_key
    form.values.data = key_infos.conf_value
    form.jira_id.data = key_infos.jira_id
    form.branch_name.data = key_infos.branch_name
    form.description.data = key_infos.description

    return render_template('config/key_value_edit.html', form=form)


'''
配置项值删除
'''

@config.route('/key_value_del', methods=['GET', 'POST'])
@login_required
def key_value_del():
    id_json = request.get_json()
    id = id_json['data']
    conf_key_value = Cmdb_conf_key_value.query.get_or_404(id)
    db.session.delete(conf_key_value)
    db.session.commit()


'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''


'''
配置项检查
'''

@config.route('/special_key', methods=['GET', 'POST'])
@login_required
def special_key():
    system_id = request.args.get('system_id', "all", type=str)
    conf_file = request.args.get('conf_file', 'all', type=str)
    conf_key = request.args.get('conf_key', '', type=str)

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    systems.append(("all", u'全部子系统'))

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.filter_by(status="special")]
    files.append(("all", u'全部文件'))

    form = QueryKeyForm(request.form, systems=system_id, files=conf_file, keys=conf_key)

    form.systems.choices = systems
    form.files.choices = files

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('system_id') or \
                     request.args.get('conf_file') or request.args.get('conf_key') is not None):
        print "1"
        if form.validate_on_submit():
            print "2"
            system_id = form.systems.data
            conf_file = form.files.data
            conf_key = form.keys.data
            page = 1
        else:
            print "3"
            system_id = request.args.get('system_id')
            conf_file = request.args.get('conf_file')
            conf_key = request.args.get('conf_key')
            form.systems.data = system_id
            form.files.data = conf_file
            form.keys.data = conf_key
            page = request.args.get('page', 1, type=int)

        key_lists = Cmdb_conf_special_key.query.order_by(Cmdb_conf_special_key.id.desc())


        if system_id != "all" and system_id is not None:
            key_lists = key_lists.filter_by(sub_system=system_id)
        if conf_file != "all" and conf_file is not None:
            key_lists = key_lists.filter_by(conf_file=conf_file)
        if conf_key != '' and conf_key is not None:
            conf_key_like = "%" + conf_key + "%"
            print conf_key
            key_lists = key_lists.filter(Cmdb_conf_special_key.conf_key.like(conf_key_like) | Cmdb_conf_special_key.branch_name.like(conf_key_like))
            #print key_lists

        pagination_search = key_lists.paginate(page, per_page=15, error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        key_lists = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Cmdb_conf_special_key.query.order_by(Cmdb_conf_special_key.id.desc()).paginate(
            page, per_page=15,
            error_out=True)
        key_lists = pagination.items

    return render_template('config/special_key_list.html', page=page, key_lists=key_lists, \
                           system_id=system_id, conf_file=conf_file, conf_key=conf_key, pagination=pagination,
                           form=form)






'''
配置项值新增
'''

@config.route('/special_key_add', methods=['GET', 'POST'])
@login_required
def special_key_add():
    form = AddKeyForm()


    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.filter_by(status="special")]
    form.files.choices = files


    if form.validate_on_submit():
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        jira_id = form.jira_id.data
        branch_name = form.branch_name.data
        description = form.description.data

        check_key_isexsit = Cmdb_conf_special_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).\
            filter_by(conf_key=conf_key).filter_by(branch_name=branch_name).filter_by(jira_id=jira_id).first()

        if check_key_isexsit is None:
            iterm = Cmdb_conf_special_key(sub_system=sub_system,
                           conf_file=conf_file,
                           conf_key=conf_key,
                           jira_id=jira_id,
                           branch_name=branch_name,
                           description=description)

            db.session.add(iterm)
            db.session.commit()

            key_infos = Cmdb_conf_special_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).\
            filter_by(conf_key=conf_key).filter_by(branch_name=branch_name).filter_by(jira_id=jira_id).first()
            conf_key_id = key_infos.id
            values = Cmdb_conf_key_value(conf_env="stb_branch", conf_key_id=conf_key_id)
            db.session.add(values)
            db.session.commit()

            return redirect(url_for('config.special_key', conf_file=conf_file, conf_key=conf_key))
        else:
            flash(u'该key在数据库中已存在,请修改', 'danger')

    return render_template('config/special_key_add.html', form=form)


'''
配置项删除
'''

@config.route('/special_key_del', methods=['GET', 'POST'])
@login_required
def special_key_del():
    id_json = request.get_json()
    id = id_json['data']
    conf_special_key = Cmdb_conf_special_key.query.get_or_404(id)
    db.session.delete(conf_special_key)
    db.session.commit()



'''
配置项修改
'''

@config.route('/special_key_edit', methods=['GET', 'POST'])
@login_required
def special_key_edit():
    key_id = request.args.get('key_id')
    print key_id
    key_infos = Cmdb_conf_special_key.query.get_or_404(key_id)
    print key_infos.conf_file
    print key_infos.sub_system
    print key_infos.conf_key
    print key_infos.branch_name
    print key_infos.description

    form = AddKeyForm()

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files


    if form.validate_on_submit():
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        jira_id = form.jira_id.data
        branch_name = form.branch_name.data
        description = form.description.data

        db.session.query(Cmdb_conf_special_key).filter_by(id=key_id).update({"sub_system": sub_system, \
                                                                        "conf_file": conf_file, "conf_key": conf_key, \
                                                                        "branch_name": branch_name, "jira_id": jira_id, \
                                                                        "description": description})
        db.session.commit()
        return redirect(url_for('config.special_key'))

    form.files.data = key_infos.conf_file
    form.systems.data = key_infos.sub_system
    form.keys.data = key_infos.conf_key
    form.jira_id.data = key_infos.jira_id
    form.branch_name.data = key_infos.branch_name
    form.description.data = key_infos.description

    return render_template('config/special_key_edit.html', form=form)




'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''

'''
配置项值列表
'''


@config.route('/special_key_value', methods=['GET', 'POST'])
@login_required
def special_key_value():
    print "11111"
    env_id = request.args.get('env_id', "all", type=str)
    system_id = request.args.get('system_id', "all", type=str)
    conf_file = request.args.get('conf_file', 'all', type=str)
    conf_key = request.args.get('conf_key', '', type=str)


    envs = [(s.env, s.env) for s in Cmdb_env.query.filter_by(type="branch")]
    envs.append(("all", u'全部环境'))

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    systems.append(("all", u'全部子系统'))


    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.filter_by(status="special")]
    files.append(("all", u'全部文件'))


    form = QueryKeyValueForm(request.form, envs=env_id, systems=system_id, files=conf_file, keys=conf_key)

    form.envs.choices = envs
    form.systems.choices = systems
    form.files.choices = files

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('env_id') or request.args.get('system_id') or \
                     request.args.get('conf_file') or request.args.get('conf_key') is not None):
        print "1"
        if form.validate_on_submit():
            print "2"
            env_id = form.envs.data
            system_id = form.systems.data
            conf_file = form.files.data
            conf_key = form.keys.data
            page = 1
        else:
            print "3"
            env_id = request.args.get('env_id')
            system_id = request.args.get('system_id')
            conf_file = request.args.get('conf_file')
            conf_key = request.args.get('conf_key')
            form.envs.data = env_id
            form.systems.data = system_id
            form.files.data = conf_file
            form.keys.data = conf_key
            page = request.args.get('page', 1, type=int)


        key_value_lists = Cmdb_conf_special_key_value.query.join(Cmdb_conf_special_key, Cmdb_conf_special_key.id == Cmdb_conf_special_key_value.conf_key_id).add_columns(
            Cmdb_conf_special_key_value.id, Cmdb_conf_special_key_value.conf_env, Cmdb_conf_special_key_value.conf_value, \
            Cmdb_conf_special_key.sub_system, Cmdb_conf_special_key.conf_file, Cmdb_conf_special_key.conf_key, \
            Cmdb_conf_special_key.branch_name, Cmdb_conf_special_key.jira_id)

        # if env_id != "all" and env_id is not None:
        #     key_value_lists = key_value_lists.filter_by(conf_env=env_id)
        if system_id != "all" and system_id is not None:
            key_value_lists = key_value_lists.filter_by(sub_system=system_id)
        if conf_file != "all" and conf_file is not None:
            key_value_lists = key_value_lists.filter_by(conf_file=conf_file)
        if conf_key != '' and conf_key is not None:
            conf_key_like = "%" + conf_key + "%"
            key_value_lists = key_value_lists.filter(
                Cmdb_conf_special_key.conf_key.like(conf_key_like) | Cmdb_conf_special_key.branch_name.like(conf_key_like))

        pagination_search = key_value_lists.paginate(page, per_page=15, error_out=False)

    if pagination_search != 0:
        pagination = pagination_search
        key_value_lists = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        key_lists = Cmdb_conf_special_key_value.query.all()


        pagination = Cmdb_conf_special_key_value.query.join(Cmdb_conf_special_key, Cmdb_conf_special_key.id == Cmdb_conf_special_key_value.conf_key_id).add_columns(
            Cmdb_conf_special_key_value.id, Cmdb_conf_special_key_value.conf_env, Cmdb_conf_special_key_value.conf_value, \
            Cmdb_conf_special_key.sub_system, Cmdb_conf_special_key.conf_file, Cmdb_conf_special_key.conf_key, \
            Cmdb_conf_special_key.branch_name, Cmdb_conf_special_key.jira_id).paginate(
            page, per_page=15,
            error_out=True)

        key_value_lists = pagination.items

    return render_template('config/special_key_value_list.html', page=page, key_value_lists=key_value_lists, env_id=env_id, \
                           system_id=system_id, conf_file=conf_file, conf_key=conf_key, pagination=pagination,
                           form=form)


'''
配置项值新增
'''


@config.route('/special_key_value_add', methods=['GET', 'POST'])
@login_required
def special_key_value_add():
    form = AddKeyValueForm()


    envs = [(s.env, s.env) for s in Cmdb_env.query.filter_by(type="branch")]
    form.envs.choices = envs

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems


    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.filter_by(status="special")]
    form.files.choices = files



    if form.validate_on_submit():
        env = form.envs.data
        sub_system = form.systems.data
        conf_file = form.files.data
        conf_key = form.keys.data
        conf_value = form.values.data
        jira_id= form.jira_id.data
        branch_name = form.branch_name.data
        description = form.description.data

        key_infos = Cmdb_conf_special_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).filter_by(
            conf_key=conf_key).first()
        if key_infos:
            pass
        else:
            iterm_key = Cmdb_conf_special_key(sub_system=sub_system,
                                 conf_file=conf_file,
                                 conf_key=conf_key,
                                 jira_id=jira_id,
                                 branch_name=branch_name,
                                 description=description)
            db.session.add(iterm_key)
            db.session.commit()

        key_infos = Cmdb_conf_special_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=conf_file).filter_by(
            conf_key=conf_key).first()

        conf_key_id = key_infos.id

        iterm_value = Cmdb_conf_special_key_value(conf_key_id=conf_key_id,
                                     conf_env=env,
                                     conf_value=conf_value,
                                     description=description)

        db.session.add(iterm_value)
        db.session.commit()
        return redirect(url_for('config.special_key_value', conf_file=conf_file, conf_key=conf_key))

    return render_template('config/special_key_value_add.html', form=form)


'''
配置项值修改
'''


@config.route('/special_key_value_edit', methods=['GET', 'POST'])
@login_required
def special_key_value_edit():
    key_id = request.args.get('key_id')
    key_info = Cmdb_conf_special_key_value.query.get_or_404(key_id)
    env = key_info.conf_env

    key_infos = Cmdb_conf_special_key_value.query.filter_by(id=key_id).join(Cmdb_conf_special_key,
                                                               Cmdb_conf_special_key.id == Cmdb_conf_special_key_value.conf_key_id).add_columns(
        Cmdb_conf_special_key_value.id, Cmdb_conf_special_key_value.conf_env, Cmdb_conf_special_key_value.conf_value, \
        Cmdb_conf_special_key_value.description, Cmdb_conf_special_key.sub_system, Cmdb_conf_special_key.conf_file, Cmdb_conf_special_key.conf_key, \
        Cmdb_conf_special_key.branch_name, Cmdb_conf_special_key.jira_id).first()

    print key_infos

    form = AddKeyValueForm()

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    form.envs.choices = envs

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files

    print form.errors
    if form.validate_on_submit():
        #env = form.envs.data
        print "=-=-========================="
        conf_value = form.values.data
        description = form.description.data
        db.session.query(Cmdb_conf_special_key_value).filter_by(id=key_id).update({"conf_value": conf_value, \
                                                                      "description": description})
        db.session.commit()
        return redirect(url_for('config.special_key_value'))

    form.envs.data = key_infos.conf_env
    form.files.data = key_infos.conf_file
    form.systems.data = key_infos.sub_system
    form.keys.data = key_infos.conf_key
    form.values.data = key_infos.conf_value
    form.jira_id.data = key_infos.jira_id
    form.branch_name.data = key_infos.branch_name
    form.description.data = key_infos.description

    return render_template('config/special_key_value_edit.html', form=form)



'''############################################################################################################################################'''
'''############################################################################################################################################'''
'''############################################################################################################################################'''



'''
生成配置
'''

@config.route('/conf_version', methods=['GET', 'POST'])
@login_required
def conf_version():
    env_id = request.args.get('env_id', "all", type=str)
    conf_version = request.args.get('conf_version', '', type=str)

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    envs.append(("all", u'全部环境'))

    form = QueryVersionForm(request.form, envs=env_id, conf_versions=conf_version)

    form.envs.choices = envs

    pagination_search = 0

    if form.validate_on_submit() or \
            (request.args.get('env_id') or request.args.get('conf_version') is not None):
        print "1"
        if form.validate_on_submit():
            print "2"
            env_id = form.envs.data
            conf_version = form.versions.data
            page = 1
        else:
            print "3"
            env_id = request.args.get('env_id')
            conf_version = request.args.get('conf_version')
            form.envs.data = env_id
            form.versions.data = conf_version
            page = request.args.get('page', 1, type=int)

        conf_version_lists = Cmdb_conf_version.query.order_by(Cmdb_conf_version.id.desc())


        if env_id != "all" and env_id is not None:
            conf_version_lists = conf_version_lists.filter_by(sub_system=system_id)
        if conf_version != '' and conf_version is not None:
            conf_version_like = "%" + conf_version + "%"
            print conf_version
            conf_version_lists = conf_version_lists.filter(Cmdb_conf_version.conf_version.like(conf_version_like))


        pagination_search = conf_version_lists.paginate(page, per_page=15, error_out=False)


    if pagination_search != 0:
        pagination = pagination_search
        conf_version_lists = pagination_search.items
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Cmdb_conf_version.query.order_by(Cmdb_conf_version.id.desc()).paginate(
            page, per_page=15,
            error_out=True)
        conf_version_lists = pagination.items

    return render_template('config/version_list.html', page=page, conf_version_lists=conf_version_lists, \
                           env_id=env_id, conf_version=conf_version, pagination=pagination,
                           form=form)







'''
配置文件版本新增
'''

@config.route('/conf_version_add', methods=['GET', 'POST'])
@login_required
def conf_version_add():
    form = AddVersionForm()

    envs = [(s.env, s.env) for s in Cmdb_env.query.all()]
    form.envs.choices = envs


    if form.validate_on_submit():
        env = form.envs.data
        git_branch = form.git_branchs.data
        description = form.description.data
        print git_branch
        print type(git_branch)
        # 创建配置文件目录
        env_conf_version = create_conf_path(env)
        # 配置文件生成
        generate_normal_conf(env, env_conf_version, git_branch)

        generate_special_conf(env, env_conf_version, git_branch, "app-mq.properties")

        cp_conf_online(env_conf_version, env)

        versions = Cmdb_conf_version(env=env, conf_version=env_conf_version)

        db.session.add(versions)
        db.session.commit()

        update_keys_status(env, git_branch)

        return redirect(url_for('config.conf_version'))
    return render_template('config/version_add.html', form=form)




def update_keys_status(env, git_branch):
    git_branches = git_branch.split(',')
    print git_branches
    for branch_name in git_branches:
        db.session.query(Cmdb_conf_key).filter_by(branch_name=branch_name).update({"status": env})






def create_conf_path(env):
    localtime = time.strftime("%Y%m%d", time.localtime())
    version = 1
    conf_env = env
    env_version = conf_env + "_" + localtime + "_" + "V"

    all_conf_path = Cmdb_other_config.query.filter_by(iterm="all_conf_path").first()
    all_config = all_conf_path.value

    env_conf_version = env_version + str(version)
    latest_config_path = os.path.join(all_config, env_conf_version)

    while os.path.isdir(latest_config_path):
        version = version + 1
        env_conf_version = env_version + str(version)
        latest_config_path = os.path.join(all_config, env_conf_version)

    sub_system_infos = Cmdb_system.query.filter_by(flag='1')
    for sub_system_info in sub_system_infos:
        conf_system = sub_system_info.name
        conf_path = os.path.join(latest_config_path,conf_system)
        isExists = os.path.exists(conf_path)
        if not isExists:
            os.makedirs(conf_path)
        else:
            pass

    return env_conf_version


def get_condition(env, git_branch):
    git_branches = git_branch.split(',')
    branch_condition_list = []
    condition = []
    condition.append(Cmdb_conf_key.status == 'stb')
    # if env == "stb_branch" or env == "prod" or env == "stb":
    #     condition.append(Cmdb_conf_key.status == 'stb')

    if env == "sit":
        condition.append(Cmdb_conf_key.status == 'pre')
        condition.append(Cmdb_conf_key.status == 'sit')
        #edit: branch_condition.status --> sit

    elif env == "pre":
        condition.append(Cmdb_conf_key.status == 'pre')
        #edit: branch_condition.status --> pre
    else:
        pass

    condition.append(Cmdb_conf_key.status == env)
    for branch in git_branches:
        condition.append(Cmdb_conf_key.branch_name == branch)

    return condition


def generate_normal_conf(env, env_conf_version, git_branch):

    condition = get_condition(env, git_branch)

    if env == "stb_branch":
        gen_env = "stb"
    else:
        gen_env = env

    conf_infos = Cmdb_conf_key_value.query.filter_by(conf_env=gen_env).join(Cmdb_conf_key,
                                                                            Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
            Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
            Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, Cmdb_conf_key_value.conf_key_id, \
            Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id, Cmdb_conf_key.status)

    conf_infos = conf_infos.filter(or_(*condition))
    #print conf_infos

    #conf_infos = Cmdb_conf_key_value.query.filter_by(conf_env=env)

    all_conf_path = Cmdb_other_config.query.filter_by(iterm="all_conf_path").first()
    all_config = all_conf_path.value

    latest_config_path = os.path.join(all_config, env_conf_version)


    for conf_info in conf_infos:
        #print conf_info
        conf_value = conf_info.conf_value
        conf_key_id = conf_info.conf_key_id

        conf_key_infos = Cmdb_conf_key.query.filter_by(id=conf_key_id).first()
        sub_system = conf_key_infos.sub_system
        conf_file = conf_key_infos.conf_file
        conf_key = conf_key_infos.conf_key

        conf_path = os.path.join(latest_config_path, sub_system)

        if conf_file == "app-mq.properties":
            pass
        else:
            conf_file_path = os.path.join(conf_path, conf_file)
            conf_key_value = str(conf_key) + "=" + str(conf_value) + "\r\n"
            #print conf_key_value
            with open(conf_file_path, "a+") as f:
                f.write(conf_key_value)



def generate_special_conf(env, env_conf_version, git_branch, conf_file):
    all_conf_path = Cmdb_other_config.query.filter_by(iterm="all_conf_path").first()
    all_config = all_conf_path.value

    latest_config_path = os.path.join(all_config, env_conf_version)

    branchs = git_branch.split(',')

    branch_sub_systems = []
    system_branches = {}
    for branch in branchs:
        conf_special_keys = Cmdb_conf_special_key.query.filter_by(branch_name=branch).first()
        branch_sub_system = conf_special_keys.sub_system
        branch_sub_systems.append(branch_sub_system)
        system_branches[branch_sub_system] = branch

    sub_system_infos = Cmdb_system.query.filter_by(flag='1')
    for sub_system_info in sub_system_infos:
        sub_system = sub_system_info.name
        # 配置文件生成路径
        conf_path = os.path.join(latest_config_path, sub_system)
        conf_file_path = os.path.join(conf_path, conf_file)


        if sub_system in branch_sub_systems:
            #子系统对应的git branch
            branch = system_branches[sub_system]

            if str(env) == "stb_branch":
                # special 表中此git branch 分支的keys 信息
                conf_special_keys = Cmdb_conf_special_key_value.query.join(Cmdb_conf_special_key,
                                                                           Cmdb_conf_special_key.id == Cmdb_conf_special_key_value.conf_key_id).add_columns(
                    Cmdb_conf_special_key_value.id, Cmdb_conf_special_key_value.conf_env,
                    Cmdb_conf_special_key_value.conf_value, \
                    Cmdb_conf_special_key.sub_system, Cmdb_conf_special_key.conf_file, Cmdb_conf_special_key.conf_key, \
                    Cmdb_conf_special_key.branch_name, Cmdb_conf_key.jira_id, Cmdb_conf_key.status).filter_by(
                    branch_name=branch)

                special_keys = []

                for special_key in conf_special_keys:
                    s_key = special_key.conf_key
                    special_keys.append(s_key)

                # 正常表中改子系统 的keys 信息
                conf_normal_keys = Cmdb_conf_key_value.query.filter_by(conf_env="stb").join(Cmdb_conf_key,
                                                                                          Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
                    Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
                    Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
                    Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id, Cmdb_conf_key.status). \
                    filter_by(sub_system=sub_system).filter_by(conf_file="app-mq.properties")

                normal_keys = []

                for normal_key in conf_normal_keys:
                    n_key = normal_key.conf_key
                    normal_keys.append(n_key)


                for s_key in special_keys:
                    if s_key in normal_keys:
                        conf_key = s_key
                        conf_value = conf_normal_keys.filter_by(conf_key=s_key).first()
                        conf_key_value = str(conf_key) + "=" + str(conf_value.conf_value) + "\r\n"
                        with open(conf_file_path, "a+") as f:
                            f.write(conf_key_value)

                    else:
                        conf_key = s_key
                        conf_value = conf_special_keys.filter_by(conf_key=s_key).first()
                        conf_key_value = str(conf_key) + "=" + str(conf_value.conf_value) + "\r\n"
                        with open(conf_file_path, "a+") as f:
                            f.write(conf_key_value)

            else:
                print "=====-====="
                # 合并mq.consumer.listener 的 value 值
                # sepcial_key = "mq.consumer.listener"
                # normal_listener_value = conf_normal_keys.filter_by(conf_key=sepcial_key).first()
                # special_listener_value = conf_special_keys.filter_by(conf_key=sepcial_key).first()
                # normal_listener_value = normal_listener_value.conf_value
                # special_listener_value = special_listener_value.conf_value
                #
                # normal_key_info = Cmdb_conf_key.query.filter_by(conf_key=sepcial_key).filter_by(conf_file=conf_file).filter_by(sub_system=sub_system).first()
                # normal_key_id = normal_key_info.id
                #
                # normal_listener_values = normal_listener_value.split(',')
                # special_listener_values = special_listener_value.split(',')
                #
                # for special_value in special_listener_values:
                #     if sepcial_key not in normal_listener_values:
                #         normal_listener_values.append(special_value)
                #     else:
                #         pass
                #
                # listener_value = ','.join(normal_listener_values)
                #
                # print env + "111"
                # # 更新合并之后的listener值到数据库
                # db.session.query(Cmdb_conf_key_value).filter_by(conf_env=env).filter_by(conf_key_id=normal_key_id).update({"conf_value": listener_value})
                # db.session.commit()

                #根据生成的环境获取对用key值
                # sit = stb + pre + sit + branch_key
                # pre = stb + pre  + branch_key
                # prod = stb + prod + branch_key
                # stb = stb + branch_key

                #condition = get_condition(env, git_branch)

                # conf_normal_keys = Cmdb_conf_key_value.query.filter_by(conf_env=env).join(Cmdb_conf_key,
                #                                                                           Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
                #     Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
                #     Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
                #     Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id, Cmdb_conf_key.status). \
                #     filter_by(sub_system=sub_system).filter_by(conf_file="app-mq.properties").filter(*condition)

                condition = get_condition(env, git_branch)
                conf_normal_keys = Cmdb_conf_key_value.query.filter_by(conf_env=env).join(Cmdb_conf_key,
                                                                                            Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
                    Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
                    Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key, \
                    Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id, Cmdb_conf_key.status). \
                    filter_by(sub_system=sub_system).filter_by(conf_file="app-mq.properties")

                conf_infos = conf_infos.filter(or_(*condition))

                normal_keys = []

                for normal_key in conf_normal_keys:
                    n_key = normal_key.conf_key
                    normal_keys.append(n_key)

                for conf_info in conf_normal_keys:
                    conf_key = conf_info.conf_key
                    conf_value = conf_info.conf_value
                    conf_key_value = str(conf_key) + "=" + str(conf_value) + "\r\n"
                    with open(conf_file_path, "a+") as f:
                        f.write(conf_key_value)

                # for s_key in special_keys:
                #     if s_key not in normal_keys:
                #         conf_key = s_key
                #
                #         conf_key_id = Cmdb_conf_special_key.query.filter_by(conf_key=s_key).filter_by(branch_name=branch).first()
                #         conf_values = Cmdb_conf_special_key_value.query.filter_by(conf_key_id=conf_key_id.id).first()
                #         conf_value = conf_values.conf_value
                #         if conf_key != "mq.env.branch.prefix":
                #             conf_key_value = str(conf_key) + "=" + str(conf_value) + "\r\n"
                #             with open(conf_file_path, "a+") as f:
                #                 f.write(conf_key_value)
                #
                #             #将mq文件新增的key对应塞进表中
                #             iterm_key = Cmdb_conf_key(sub_system=sub_system,
                #                                    conf_file="app-mq.properties",
                #                                    conf_key=conf_key,
                #                                    branch_name=branch,
                #                                    status = 'sit')
                #
                #             db.session.add(iterm_key)
                #             db.session.commit()
                #
                #             key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file="app-mq.properties").filter_by(conf_key=conf_key).first()
                #             conf_key_id = key_infos.id
                #
                #             envs = Cmdb_env.query.filter_by(type="trunk")
                #             for env_info in envs:
                #                 env = env_info.env
                #                 iterm_value = Cmdb_conf_key_value(conf_key_id=conf_key_id,
                #                                              conf_env=env,
                #                                              conf_value=conf_value)
                #                 db.session.add(iterm_value)
                #                 db.session.commit()
                #
                #
                #     else:
                #         pass

        else:

            if str(env) == "stb_branch":
                conf_infos = Cmdb_conf_key_value.query.filter_by(conf_env="stb").join(Cmdb_conf_key,
                                                                                        Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
                    Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
                    Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key,
                    Cmdb_conf_key.branch_name,
                    Cmdb_conf_key.jira_id, Cmdb_conf_key.status).filter_by(sub_system=sub_system).filter_by(
                    conf_file=conf_file)

                for conf_info in conf_infos:
                    print conf_info
                    conf_value = conf_info.conf_value
                    conf_key = conf_info.conf_key
                    conf_key_value = str(conf_key) + "=" + str(conf_value) + "\r\n"
                    with open(conf_file_path, "a+") as f:
                        f.write(conf_key_value)

            else:

                condition = get_condition(env, git_branch)
                conf_infos = Cmdb_conf_key_value.query.filter_by(conf_env=env).join(Cmdb_conf_key,
                                                                                        Cmdb_conf_key.id == Cmdb_conf_key_value.conf_key_id).add_columns(
                    Cmdb_conf_key_value.id, Cmdb_conf_key_value.conf_env, Cmdb_conf_key_value.conf_value, \
                    Cmdb_conf_key.sub_system, Cmdb_conf_key.conf_file, Cmdb_conf_key.conf_key,
                    Cmdb_conf_key_value.conf_key_id, \
                    Cmdb_conf_key.branch_name, Cmdb_conf_key.jira_id, Cmdb_conf_key.status)

                conf_infos = conf_infos.filter(or_(*condition)).filter_by(sub_system=sub_system).filter_by(conf_file=conf_file)

                for conf_info in conf_infos:
                    print conf_info
                    conf_value = conf_info.conf_value
                    conf_key = conf_info.conf_key
                    conf_key_value = str(conf_key) + "=" + str(conf_value) + "\r\n"
                    with open(conf_file_path, "a+") as f:
                        f.write(conf_key_value)



def cp_conf_online(env_conf_version, env):

    online_config_path = Cmdb_other_config.query.filter_by(iterm="online_conf_path").first()
    online_path = online_config_path.value

    online_conf_path = os.path.join(online_path, env)

    all_conf_path = Cmdb_other_config.query.filter_by(iterm="all_conf_path").first()
    all_config = all_conf_path.value

    latest_config_path = os.path.join(all_config, env_conf_version)


    if os.path.isdir(online_conf_path):
        shutil.rmtree(online_conf_path)
    else:
        pass
    shutil.copytree(latest_config_path, online_conf_path)

    db.session.query(Cmdb_env).filter_by(env=env).update({"version": env_conf_version})
    db.session.commit()



'''
配置文件版本回退
'''

@config.route('/version_rollback', methods=['GET', 'POST'])
@login_required
def version_rollback():
    version_id = request.args.get('version_id')
    env = Cmdb_env.query.get_or_404(version_id)
    version_infos = Cmdb_conf_version.query.get_or_404(version_id)
    env_conf_version = version_infos.conf_version
    env = version_infos.env
    if env is not None:
        flash(u'%s已是当前版本,无需回退' % env_conf_version, 'success')
        return redirect(url_for('config.conf_version'))
    else:
        cp_conf_online(env_conf_version, env)
        flash(u'配置文件已回退到%s' % env_conf_version, 'success')
        return redirect(url_for('config.conf_version'))



'''
配置文件版本删除
'''

@config.route('/conf_version_del', methods=['GET', 'POST'])
@login_required
def conf_version_del():
    id_json = request.get_json()
    id = id_json['data']
    print "===="
    print id
    print "===="
    conf_version = Cmdb_conf_file.query.get_or_404(id)
    db.session.delete(conf_version)
    db.session.commit()



'''
配置项检查
'''

@config.route('/key_check', methods=['GET', 'POST'])
@login_required
def key_check():
    form = CheckKeyForm()

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    if form.validate_on_submit():
        sub_system = form.systems.data
        git_tag_path = form.path.data
        compare_results = []

        git_paths = Cmdb_system.query.filter_by(name=sub_system).first()
        git_org_path = git_paths.conf_git_url
        git_path = git_org_path.replace("{branch_id}", git_tag_path)

        git_token = Cmdb_other_config.query.filter_by(iterm="git_private_token").first()
        git_private_token = git_token.value

        cmdb_conf_files = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id)

        for cmdb_conf_file in cmdb_conf_files:

            cmdb_conf_file_path = cmdb_conf_file.conf_file + "?private_token=" + git_private_token
            git_sub_system_conf_keys = get_git_conf_key(git_path, cmdb_conf_file_path)
            git_sub_system_conf_values = get_git_conf_value(git_path, cmdb_conf_file_path)

            if cmdb_conf_file.conf_file == "app-mq.properties":
                print "1"
                print git_sub_system_conf_keys
                if git_sub_system_conf_keys:
                    print "2"
                    for conf_key in git_sub_system_conf_keys:
                        special_key = Cmdb_conf_special_key.query.filter_by(conf_key=conf_key).filter_by(branch_name=git_tag_path).first()
                        #print "3"
                        if special_key is None:
                            iterm_key = Cmdb_conf_special_key(sub_system=sub_system,
                                             conf_file=cmdb_conf_file.conf_file,
                                             conf_key=conf_key,
                                             branch_name=git_tag_path,
                                             status='stb_branch')

                            db.session.add(iterm_key)
                            db.session.commit()

                            key_infos = Cmdb_conf_special_key.query.filter_by(sub_system=sub_system).filter_by(
                                conf_file=cmdb_conf_file.conf_file).filter_by(conf_key=conf_key).first()
                            conf_key_id = key_infos.id

                            conf_value = git_sub_system_conf_values[conf_key]

                            print conf_key + "=" + conf_value
                            iterm_value = Cmdb_conf_special_key_value(conf_key_id=conf_key_id,
                                                         conf_env="stb_branch", conf_value=conf_value)
                            db.session.add(iterm_value)
                            db.session.commit()
                else:
                    flash_info = "%s分支,%s文件无法找到,请确定分支和子系统是否正确" % (git_tag_path, cmdb_conf_file.conf_file)
                    flash(u'%s' % flash_info, 'danger')
            else:
                pass

            cmdb_sub_system_conf_keys = get_cmdb_conf(sub_system, cmdb_conf_file.conf_file)
            difference = set(git_sub_system_conf_keys).difference(set(cmdb_sub_system_conf_keys))
            compare_result = list(difference)

            if git_sub_system_conf_keys:
                if compare_result:
                    compare_results.append(compare_result)
                    for conf_key in compare_result:
                        iterm_key = Cmdb_conf_key(sub_system=sub_system, conf_file=cmdb_conf_file.conf_file,
                                             conf_key=conf_key, branch_name=git_tag_path, status = 'stb_branch')
                        db.session.add(iterm_key)
                        db.session.commit()

                        key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=cmdb_conf_file.conf_file).filter_by(conf_key=conf_key).first()
                        conf_key_id = key_infos.id

                        envs = Cmdb_env.query.filter_by(type="trunk")
                        for env_info in envs:
                            env = env_info.env
                            iterm_value = Cmdb_conf_key_value(conf_key_id=conf_key_id, conf_env=env)
                            db.session.add(iterm_value)
                            db.session.commit()
                else:
                    pass
            else:
                flash_info = "%s分支,%s文件无法找到,请确定分支和子系统是否正确" % (git_tag_path, cmdb_conf_file.conf_file)
                flash(u'%s' % flash_info, 'danger')


        git_result = Cmdb_conf_key.query.filter_by(branch_name=git_tag_path).first()

        if git_sub_system_conf_keys:
            print git_sub_system_conf_keys[0]
            if git_result is not None:
            #if compare_results:
                return redirect(url_for('config.key', system_id='all', conf_file='all', conf_key=git_tag_path))
            else:
                flash(u'%s分支无新增配置项' % git_tag_path, 'success')
        else:
            pass

    return render_template('config/key_value_check.html', form=form)



def get_git_conf_key(url, conf_file):
    git_url = os.path.join(url, conf_file)
    git_conf_list = []
    html = requests.get(git_url)
    print git_url
    #print html.text
    print html.status_code
    if html.status_code == 200:
        info = html.text
        info_lists = info.split('\n')

        for info_list in info_lists:
            pattern = re.compile('(^\w.*?)=')
            news = pattern.findall(info_list)
            if news:
                new = news[0]
                git_conf_list.append(new)
        print "222222222222222222222"
        print git_conf_list
        return git_conf_list
    else:
        print git_conf_list
        print "123123123123123213213"
        return git_conf_list


def get_git_conf_value(url, conf_file):
    git_url = os.path.join(url, conf_file)
    #git_conf_key_list = []
    git_dict = {}
    html = requests.get(git_url)
    if html.status_code == 200:
        info = html.text
        info_lists = info.split('\n')

        for info_list in info_lists:
            pattern_key = re.compile('(^\w.*?)=')
            pattern_value = re.compile('^\w.*?=(.*)')
            keys = pattern_key.findall(info_list)
            values = pattern_value.findall(info_list)
            #print news
            if keys and values:
                key = keys[0]
                value = values[0]
                git_dict[key] = value
                #git_conf_value_list.append(new)
        return git_dict
    else:
        return git_dict


def get_conf_key(sub_system, conf_file):
    sql = "select conf_key from cmdb_conf_key where sub_system = '%s' and conf_file = '%s';"
    select_sql = sql % (sub_system, conf_file)
    conf_keys = db.session.execute(select_sql)
    return conf_keys



def get_cmdb_conf(sub_system, conf_file):
    conf_keys = []
    conf_info = get_conf_key(sub_system, conf_file)
    for conf_key in conf_info:
        conf_keys.append(conf_key[0])
    return conf_keys


def compare_conf(cmdb_conf_list, git_conf_list):
    difference = set(git_conf_list).difference(set(cmdb_conf_list))
    conf_difference = list(difference)
    return conf_difference













'''
配置项值修改
'''

@config.route('/key_value_batch_edit', methods=['GET', 'POST'])
@login_required
def key_value_batch_edit():
    key_id = request.args.get('key_id')
    print key_id
    key_infos = Cmdb_conf_key.query.get_or_404(key_id)
    key_value_infos = Cmdb_conf_key_value.query.filter_by(conf_key_id=key_id)
    envs = Cmdb_env.query.filter_by(type="trunk")
    print key_infos.jira_id
    form = BatchAddKeyValueForm()

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    files = [(s.conf_file, s.conf_file) for s in Cmdb_conf_file.query.all()]
    form.files.choices = files


    if form.validate_on_submit():
        print "1-1"
        for env_info in key_value_infos:
            env = env_info.conf_env
            conf_value = request.form[env]
            print conf_value
            db.session.query(Cmdb_conf_key_value).filter_by(conf_key_id=key_id, conf_env=env).update({"conf_value": conf_value})
            db.session.commit()

        return redirect(url_for('config.key_value', conf_key=key_infos.conf_key, system_id=key_infos.sub_system))


    form.files.data = key_infos.conf_file
    form.systems.data = key_infos.sub_system
    form.keys.data = key_infos.conf_key
    form.jira_id.data = key_infos.jira_id
    form.branch_name.data = key_infos.branch_name
    form.description.data = key_infos.description


    return render_template('config/key_value_batch_edit.html', form=form, key_value_infos=key_value_infos)




@config.route('/init_config', methods=['GET', 'POST'])
@login_required
def init_config():
    form = CheckKeyForm()

    systems = [(s.name, s.name) for s in Cmdb_system.query.filter_by(flag="1").all()]
    form.systems.choices = systems

    if form.validate_on_submit():
        sub_system = form.systems.data
        git_tag_path = form.path.data
        compare_results = []

        git_paths = Cmdb_system.query.filter_by(name=sub_system).first()
        git_org_path = git_paths.conf_git_url
        git_path = git_org_path.replace("{branch_id}", git_tag_path)

        git_token = Cmdb_other_config.query.filter_by(iterm="git_private_token").first()
        git_private_token = git_token.value

        cmdb_conf_files = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id)

        for cmdb_conf_file in cmdb_conf_files:
            conf_file = cmdb_conf_file.conf_file
            # cmdb_conf_file_path = cmdb_conf_file.conf_file + "?private_token=" + git_private_token
            # git_sub_system_conf_keys = get_git_conf_key(git_path, cmdb_conf_file_path)
            # git_sub_system_conf_values = get_git_conf_value(git_path, cmdb_conf_file_path)
            conf_file = cmdb_conf_file.conf_file
            write_file(git_path, sub_system, conf_file)
            insert_db(sub_system, conf_file)


    return render_template('config/init_config.html', form=form)


# @config.route('/generate_conf', methods=['GET', 'POST'])
# def generate_conf():
#     localtime = time.strftime("%Y%m%d", time.localtime())
#     version = 1
#     #env_id = request.args.get('env_id')
#     conf_env = request.args.get('env_id')
#     env_version = conf_env + "_" + localtime + "_" + "V"
#
#     all_conf_path = Cmdb_other_config.query.filter_by(iterm="all_conf_path").first()
#     all_config = all_conf_path.value
#
#     latest_config_path1 = os.path.join(all_config, env_version)
#     latest_config_path = latest_config_path1 + str(version)
#
#     while os.path.isdir(latest_config_path):
#         version = version + 1
#         latest_config_path = latest_config_path1 + str(version)
#
#
#     sub_system_infos = Cmdb_system.query.order_by(Cmdb_system.id)
#     for sub_system_info in sub_system_infos:
#         conf_system = sub_system_info.sub_system
#         conf_path = os.path.join(latest_config_path,conf_system)
#         isExists = os.path.exists(conf_path)
#         if not isExists:
#             os.makedirs(conf_path)
#         else:
#             pass
#
#
#     conf_infos = Cmdb_conf_key_value.query.filter_by(conf_env=conf_env)
#
#     for conf_info in conf_infos:
#         conf_value = conf_info.conf_value
#         conf_key_id = conf_info.conf_key_id
#
#         conf_key_infos = Cmdb_conf_key.query.filter_by(id=conf_key_id).first()
#         sub_system = conf_key_infos.sub_system
#         conf_file = conf_key_infos.conf_file
#         conf_key = conf_key_infos.conf_key
#
#         conf_path = os.path.join(latest_config_path, sub_system)
#         conf_file_path = os.path.join(conf_path, conf_file)
#         print conf_file_path
#         conf_key_value = str(conf_key) + "=" + str(conf_value) + "\r\n"
#         with open(conf_file_path, "a+") as f:
#             f.write(conf_key_value)
#
#
#
#     online_config_path = Cmdb_other_config.query.filter_by(iterm="online_conf_path").first()
#     online_path = online_config_path.value
#
#     online_conf_path = os.path.join(online_path, conf_env)
#
#     if os.path.isdir(online_conf_path):
#         shutil.rmtree(online_conf_path)
#     else:
#         pass
#     shutil.copytree(latest_config_path, online_conf_path)
#
#     env_version = env_version + str(version)
#     db.session.query(Cmdb_env).filter_by(env=conf_env).update({"version": env_version})
#     db.session.commit()
#
#
#     return redirect(url_for('config.env'))




@config.route('/config_text', methods=['GET', 'POST'])
def config_text():
    online_config_path = Cmdb_other_config.query.filter_by(iterm="online_conf_path").first()
    config_path = online_config_path.value

    infos = ''
    root_path = config_path
    ajax_info = request.get_json()
    ajax_path = ajax_info['data']
    path = os.path.join(root_path, ajax_path)
    # path = root_path + ajax_path
    if 'properties' in path:
        if 'app-database.properties' in path:
            file_object = open(path)
            try:
                infos = file_object.read()
            finally:
                file_object.close()

            infos = infos.replace('<', '&lt;').replace('>', '&gt;')

            # pattern = 'db.password=(.*)'
            # out = re.sub(pattern, 'db.password=*************', infos)
            pattern = 'db.password=(.*)'
            infos = re.sub(pattern, 'db.password=*************', infos)

            pattern2 = 'db.password2=(.*)'
            infos = re.sub(pattern2, 'db.password2=*************', infos)

            pattern3 = 'db.password3=(.*)'
            infos = re.sub(pattern3, 'db.password3=*************', infos)

            return jsonify({'test': infos})


        else:
            file_object = open(path)
            try:
                infos = file_object.read()
            finally:
                file_object.close()

            infos = infos.replace('<','&lt;').replace('>','&gt;')
            #print infos
            return jsonify({'test': infos})
    else:
        return jsonify({'test': infos})


# @config.route('/config_tree', methods=['GET', 'POST'])
# def config_tree():
#
#     online_config_path = Cmdb_other_config.query.filter_by(iterm="online_conf_path").first()
#     config_path = online_config_path.value
#
#     jsonstr = get_tree_json.fun(config_path,0)
#     jsonstr+="]"
#     print json
#     return jsonstr

@config.route('/config_tree', methods=['GET', 'POST'])
def config_tree():
    try:
        online_config_path = Cmdb_other_config.query.filter_by(iterm="online_conf_path").first()
        config_path = online_config_path.value
        #jsonstrs = ''
        jsonstrs = get_tree_json.fun(config_path,0,0,"[")
        jsonstrs+="]"
        print jsonstrs
        return jsonstrs
    except Exception, e:
        print e



@config.route('/config', methods=['GET', 'POST'])
def config():

    return render_template('config/code_editor.html')








'''##############################################################################'''
'''##############################################################################'''
'''##############################################################################'''
'''##############################################################################'''
'''##############################################################################'''










def write_file(url,sub_system, conf_file):
    git_private_token = "gpMHRnx86igww4hEMTUe"
    conf_file_path = conf_file + "?private_token=" + git_private_token
    git_url = os.path.join(url, conf_file_path)
    html = requests.get(git_url)
    replace_file_root_path = "/Users/gufy/Desktop/cmdb_conf/replace/"
    replace_file_sub_system_path = os.path.join(replace_file_root_path, sub_system)
    replace_file_path = os.path.join(replace_file_sub_system_path, conf_file)
    isExists = os.path.exists(replace_file_sub_system_path)
    if not isExists:
        os.makedirs(replace_file_sub_system_path)
    else:
        pass

    if html.status_code == 200:
        info = html.text
        info_lists = info.split('\n')
        for line in info_lists:
            pattern = re.compile(r'(^[^#].*)\\$')
            infos = pattern.findall(line)
            print infos
            if infos:
                infos = infos[0]
                infos = infos.replace("\\", "")
                print infos
                infos = infos.replace("\n", "")
                with open(replace_file_path, "a+") as f:
                    f.write(infos)
            else:
                with open(replace_file_path, "a+") as f:
                    line = line + "\n"
                    f.write(line)
    else:
        pass


def insert_db(sub_system, conf_file):

    replace_file_root_path = "/Users/gufy/Desktop/cmdb_conf/replace/"
    replace_file_sub_system_path = os.path.join(replace_file_root_path, sub_system)
    replace_file_path = os.path.join(replace_file_sub_system_path, conf_file)

    for line in open(replace_file_path):
        info = line
        info_lists = info.split('\n')

        for info_list in info_lists:
            pattern_key = re.compile('(^\w.*?)=')
            pattern_value = re.compile('^\w.*?=(.*)')
            keys = pattern_key.findall(info_list)
            values = pattern_value.findall(info_list)
            #print news
            if keys and values:
                conf_key = keys[0]
                conf_value = values[0]
                #git_dict[key] = value
                iterm_key = Cmdb_conf_key(sub_system=sub_system, conf_file=conf_file,
                                     conf_key=conf_key,status='init')
                db.session.add(iterm_key)
                db.session.commit()

                key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(
                    conf_file=conf_file).filter_by(conf_key=conf_key).first()
                conf_key_id = key_infos.id

                envs = Cmdb_env.query.filter_by(type="trunk")
                for env_info in envs:
                    env = env_info.env
                    iterm_value = Cmdb_conf_key_value(conf_key_id=conf_key_id, conf_env=env, conf_value=conf_value)
                    db.session.add(iterm_value)
                    db.session.commit()


