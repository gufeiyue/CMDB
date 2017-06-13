# coding:utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from . import api
from flask import jsonify, request, abort
from ..models import Cmdb_conf_file, Cmdb_conf_key, Superlight_config, Cmdb_conf_key_value, Cmdb_system, Cmdb_other_config, Cmdb_conf_special_key,\
Cmdb_conf_special_key_value, Cmdb_env
from ..config.views import get_cmdb_conf, get_git_conf_key, get_git_conf_value
import json
from .. import db


@api.route('/check_config', methods=['POST'])
def check_config():
    # if not request.get_json() or not 'jira_id' in request.get_json():
    #     abort(400)
    json_api = request.get_json()
    jira_id = json_api["jira_id"]
    config_infos = json_api["config_info"]

    git_check_result = git_check(json_api)
    if git_check_result == "git check sucess":
        insert_config(json_api)
        for sub_system in config_infos:
            git_tag_path = config_infos[sub_system]["branch_name"]
            compare_result = compare_add_key(git_tag_path)
            if compare_result == "compare keys sucess":
                super_conf_infos = Superlight_config.query.filter_by(jira_id=jira_id)
                for super_conf_info in super_conf_infos:
                    branch_name = super_conf_info.branch_name
                    sub_system = super_conf_info.sub_system
                    file_name = super_conf_info.file_name
                    key = super_conf_info.key
                    value = super_conf_info.value
                    env = super_conf_info.env
                    operation = super_conf_info.operation
                    if operation == "add":
                        add_cmdb_key(jira_id, branch_name, sub_system, file_name, key, value, env)
                    elif operation == "edit":
                        edit_cmdb_key(sub_system, file_name, key, value, env)
                    else:
                        delete_cmdb_key(sub_system, file_name, key, value, env)
                return jsonify({'check_config_reslut': "sucess"}), 200
            else:
                return jsonify(compare_result), 400
    else:
        git_check_results = {}
        git_check_results["can't find git branch or config file"] = git_check_result
        return jsonify(git_check_results), 400




def git_check(json_api):
    print type(json_api)
    jira_id = json_api["jira_id"]
    print jira_id
    config_infos = json_api["config_info"]
    error_file_messages = {}
    for sub_system in config_infos:
        git_tag_path = config_infos[sub_system]["branch_name"]
        compare_results = []
        print sub_system
        git_paths = Cmdb_system.query.filter_by(sub_system=sub_system).first()
        git_org_path = git_paths.git_root_path
        git_path = git_org_path.replace("{branch_id}", git_tag_path)

        git_token = Cmdb_other_config.query.filter_by(iterm="git_private_token").first()
        git_private_token = git_token.value

        cmdb_conf_files = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id)

        git_files = []

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
                        special_key = Cmdb_conf_special_key.query.filter_by(conf_key=conf_key).filter_by(version=git_tag_path).first()
                        #print "3"
                        if special_key is None:
                            iterm_key = Cmdb_conf_special_key(sub_system=sub_system,
                                             conf_file=cmdb_conf_file.conf_file,
                                             conf_key=conf_key,
                                             version=git_tag_path,
                                             status='E')

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
                    #flash(u'%s' % flash_info, 'danger')
                    git_files.append(cmdb_conf_file.conf_file)
                    #print flash_info


            else:
                cmdb_sub_system_conf_keys = get_cmdb_conf(sub_system, cmdb_conf_file.conf_file)
                difference = set(git_sub_system_conf_keys).difference(set(cmdb_sub_system_conf_keys))
                compare_result = list(difference)

                if git_sub_system_conf_keys:
                    if compare_result:
                        compare_results.append(compare_result)
                        for conf_key in compare_result:
                            iterm_key = Cmdb_conf_key(sub_system=sub_system, conf_file=cmdb_conf_file.conf_file,
                                                 conf_key=conf_key, version=git_tag_path, status = 'E')
                            db.session.add(iterm_key)
                            db.session.commit()

                            key_infos = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=cmdb_conf_file.conf_file).filter_by(conf_key=conf_key).first()
                            conf_key_id = key_infos.id

                            envs = Cmdb_env.query.order_by(Cmdb_env.id)
                            for env_info in envs:
                                env = env_info.env
                                iterm_value = Cmdb_conf_key_value(conf_key_id=conf_key_id, conf_env=env)
                                db.session.add(iterm_value)
                                db.session.commit()
                    else:
                        pass
                else:
                    #print flash_info
                    git_files.append(cmdb_conf_file.conf_file)
                    #flash(u'%s' % flash_info, 'danger')

        if git_files:
            error_file_messages[git_tag_path] = git_files
            return error_file_messages
        else:
            return "git check sucess"



def insert_config(json_api):
    print type(json_api)
    jira_id = json_api["jira_id"]
    print jira_id
    config_infos = json_api["config_info"]
    for sub_system in config_infos:
        conf_file = config_infos[sub_system]
        for filename in conf_file:
            branch_name = conf_file["branch_name"]
            if filename != "branch_name":
                conf_keys = conf_file[filename]
                for key in conf_keys:
                    conf_value = conf_keys[key]
                    operation = conf_value["operation"]
                    if operation == "add":
                        for env in conf_value:
                            #print env
                            if env != "operation":
                                key_value = conf_value[env]
                                insert_into_super_config(jira_id, branch_name, sub_system, filename, key, key_value, env, "add")

                    elif operation == "edit":
                        for env in conf_value:
                            if env != "operation":
                                key_value = conf_value[env]
                                insert_into_super_config(jira_id, branch_name, sub_system, filename, key, key_value, env, "edit")
                    else:
                        for env in conf_value:
                            if env != "operation":
                                insert_into_super_config(jira_id, branch_name, sub_system, filename, key, "", env, "delete")
            else:
                pass



def insert_into_super_config(jira_id, branch_name, sub_system, filename, key, key_value, env, operation):
    print jira_id, branch_name, sub_system, filename, key, key_value, env, operation
    conf_info = Superlight_config.query.filter_by(jira_id=jira_id).filter_by(branch_name=branch_name).\
        filter_by(sub_system=sub_system).filter_by(file_name=filename).\
        filter_by(key=key).filter_by(operation=operation).filter_by(env_name=env).first()
    if conf_info is None:
        config = Superlight_config(jira_id=jira_id, branch_name=branch_name, sub_system=sub_system, \
                                       file_name=filename, key=key, value=key_value, \
                                       env_name=env, operation=operation)
        db.session.add(config)
        db.session.commit()



def compare_add_key(branch_name):
    cmdb_keys = Cmdb_conf_key.query.filter_by(version=branch_name)
    super_config_keys = Superlight_config.query.filter_by(branch_name=branch_name).filter_by(env_name="prod")

    cmdb_new_keys = []
    for cmdb_key in cmdb_keys:
        cmdb_new_keys.append(cmdb_key)

    if "mq.env.branch.prefix" in cmdb_new_keys:
        cmdb_new_keys.remove("mq.env.branch.prefix")

    super_new_keys = []
    for super_key in super_config_keys:
        super_new_keys.append(super_key)

    difference_in_git = set(super_new_keys).difference(set(cmdb_new_keys))
    difference_in_cmdb = set(cmdb_new_keys).difference(set(super_new_keys))
    compare_result_git = list(difference_in_git)
    compare_result_cmdb = list(difference_in_cmdb)
    compare_result = {}
    if compare_result_git:
        compare_result["in_cmdb_no_git"] = compare_result_git
    if compare_result_cmdb:
        compare_result["in_git_no_cmdb"] = compare_result_cmdb

    if compare_result_cmdb and compare_result_git:
        return compare_result
    else:
        return "compare keys sucess"


def add_cmdb_key(jira_id, branch_name, sub_system, file_name, key, value, env):
    #print jira_id, branch_name, sub_system, filename, key, key_value, env
    #super_conf_key_infos = Superlight_config.query.filter_by(jira_id=jira_id).filter_by(operation="add")
    #jira_id, branch_name, sub_system, file_name, key, value, env
    conf_key_info = Cmdb_conf_key.query.filter_by(jira_id=jira_id).filter_by(version=branch_name).\
        filter_by(sub_system=sub_system).filter_by(conf_file=file_name).\
        filter_by(key=key).first()

    if conf_key_info is not None:
        conf_key_id = conf_key_info.id
        db.session.query(Cmdb_conf_key_value).filter_by(conf_key_id=conf_key_id).filter_by(env=env).update({"conf_value": value})
        db.session.commit()


def edit_cmdb_key(jira_id, sub_system, file_name, key, value, env):
    #edit_key_infos = Superlight_config.query.filter_by(jira_id=jira_id).filter_by(operation="edit")
    #error_messages = []
    #for edit_key in edit_key_infos:
        # sub_system = edit_key.sub_system
        # filename = edit_key.file_name
        # key = edit_key.key
        # value = edit_key.value
        # env_name = edit_key.env_name

    conf_key_info = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=file_name).filter_by(conf_key=key).first()
    if conf_key_info is not None:
        conf_key_id = conf_key_info.id
        db.session.query(Cmdb_conf_key_value).filter_by(conf_key_id=conf_key_id).filter_by(conf_file=file_name).filter_by(conf_env=env).update(
            {"conf_value": value})
        db.session.commit()
    # else:
    #     error_messages.append(key)
    # if error_messages:
    #     error_messages = ",".join(error_messages)
    #     error_messages = "%s key 在 cmdb 中不存在" %  error_messages
    #     return error_messages
    # else:
    #     return "edit keys sucess"


def delete_cmdb_key(jira_id, sub_system, file_name, key, env):
    conf_key_info = Cmdb_conf_key.query.filter_by(sub_system=sub_system).filter_by(conf_file=file_name).filter_by(conf_key=key).first()
    db.session.delete(conf_key_info)





#curl -i -H "Content-Type: application/json" -X POST -d '{"title":"Read a book"}' http://localhost:5000/todo/api/v1.0/tasks

@api.route('/tasks', methods=['POST'])
def create_task():
    if not request.get_json() or not 'env' in request.get_json():
        abort(400)
    env = request.get_json()["env"]
    git_branches =  request.get_json()["git_branches"]
    cmdb_conf_files = Cmdb_conf_file.query.order_by(Cmdb_conf_file.id)

    branch_list = git_branches.split(',')

    cmdb_keys = []
    for branch in branch_list:
        keys = Cmdb_conf_key.query.filter_by(version=branch)
        key = keys.conf_key
        cmdb_keys.append(key)


    for conf_files in cmdb_conf_files:
        conf_file = conf_files.conf_file
        key_infos = request.get_json()["config"]["sit"][conf_file]

        for (key,value) in key_infos.items():
            print key + "=" + value


    print env
    print git_branches
    #print app_caches

    return jsonify({'env': env}), 201

# @api.route('/users/<int:id>')
# def get_user(id):
#     user = User.query.get_or_404(id)
#     return jsonify(user.to_json())