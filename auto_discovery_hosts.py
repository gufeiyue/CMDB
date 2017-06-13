#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, re, Queue
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import threading,subprocess

from collections import namedtuple
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.parsing.dataloader import DataLoader

reload(sys)
sys.setdefaultencoding('utf-8')

queue=Queue.Queue()


# 创建对象的基类:
Base = declarative_base()
# 初始化数据库连接:
engine = create_engine('mysql://root:123456@192.168.5.2:3306/superlight?charset=utf8', encoding='utf-8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
session = DBSession()



'''
====================================================================
自定义ansible输出
====================================================================
'''

class ResultCallback(CallbackBase):
    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        ip = host.name
        asset_infos = {}
        asset_infos[ip] = result._result
        update_asset(asset_infos, ip)


'''
====================================================================
Models:
====================================================================
'''

class Cmdb_hostbase(Base):
    Column(String(64))
    __tablename__ = 'cmdb_hostbase'
    id = Column(Integer, primary_key=True)
    hostname = Column(String((32)), default='')
    ip = Column(String((20)))
    cpu = Column(String((32)))
    memory = Column(String((32)))
    disk = Column(String((32)))
    machine_type = Column(String((16)))
    os = Column(String((32)))
    host_status = Column(String((16)))
    install_path = Column(String((255)))
    env_id = Column(Integer)
    service_id = Column(Integer)
    system_id = Column(Integer)


class Cmdb_acc_info(Base):
    __tablename__ = 'cmdb_acc_info'
    id = Column(Integer, primary_key=True)
    ip = Column(String((32)))
    username = Column(String((32)))
    password = Column(String((32)))
    host_status = Column(String((11)))
    result = Column(Integer)
    type = Column(String((32)))


class Cmdb_net_segment_list(Base):
    __tablename__ = 'cmdb_net_segment_list'
    id = Column(Integer, primary_key=True)
    segment = Column(String((20)))
    status = Column(String((1)))



'''
====================================================================
01、判断ip是否存活,修改数据库状态
====================================================================
'''

class ThreadUrl(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue=queue

    def run(self):
        while True:
            sessions = DBSession()
            host=self.queue.get()
            ret=subprocess.call('ping -c 1 '+host,shell=True,stdout=open('/dev/null','w'))
            if ret:
                # info = "%s is down" % host
                #print info
                try:
                    ip_info = sessions.query(Cmdb_hostbase).filter_by(ip=host).first()
                    if ip_info:
                        sessions.query(Cmdb_hostbase).filter_by(ip=host).update({Cmdb_hostbase.host_status: 'off'})
                        sessions.query(Cmdb_acc_info).filter_by(ip=host).update({Cmdb_acc_info.host_status: 'off'})
                        sessions.commit()
                    else:
                        pass
                except Exception, e:
                    print "++++++++++++++++++", e.message
                finally:
                    sessions.close()

            else:
                # info = "%s is up" % host
                # print info
                try:
                    ip_info = sessions.query(Cmdb_hostbase).filter_by(ip=host).first()
                    if ip_info:
                        sessions.query(Cmdb_hostbase).filter_by(ip=host).update({Cmdb_hostbase.host_status: 'on'})
                        sessions.query(Cmdb_acc_info).filter_by(ip=host).update({Cmdb_acc_info.host_status: 'on'})
                        sessions.commit()
                    else:
                        hostbase_info = Cmdb_hostbase(ip=host, host_status='on')
                        sessions.add(hostbase_info)
                        sessions.commit()
                        acc_info = Cmdb_acc_info(ip=host, result='0', host_status='on')
                        sessions.add(acc_info)
                        sessions.commit()
                except Exception, e:
                    print "=================", e.message
                finally:
                    sessions.close()
            self.queue.task_done()


def ping_ip(network_segment):
    for i in range(100):
        t=ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

    for x in range(1, 255):
        ip = network_segment + str(x)
        queue.put(ip)
    queue.join()



'''
====================================================================
02、验证用户名密码
====================================================================
'''

def verify_password(network_segment):
    echo_command = "echo '[all]' > verify_password"
    os.system(echo_command)
    network_segment_like = "%" + network_segment + "%"
    print network_segment_like
    acc_infos = session.query(Cmdb_acc_info).filter_by(host_status='on').filter_by(result='1').filter(Cmdb_acc_info.ip.like(network_segment_like))
    host_info = acc_infos.first()
    if host_info:
        for acc_info in acc_infos:
            ip = acc_info.ip
            print ip
            username = acc_info.username
            password = acc_info.password
            ansible_info = ip + " ansible_ssh_user=" + username + " ansible_ssh_pass='" + password + "' ansible_sudo_pass='" + password + "'\n"
            with open('verify_password', "a+") as f:
                f.write(ansible_info)
        ansible_verify_password()
    else:
        pass

def ansible_verify_password():
    ansible = "ansible -i verify_password all -m shell -a 'hostname' -f 80 -o"
    infos = os.popen(ansible)
    results = infos.readlines()

    for info in results:
        ip_re = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
        # print info
        result_re = re.compile(r'(.*UNREACHABLE.*)')
        ips = result_re.findall(info)
        if ips:
            sucess_reult = ips[0]
            sucess_ip = ip_re.findall(sucess_reult)
            ip = sucess_ip[0]
            print ip
            if ip:
                print ip
                session.query(Cmdb_acc_info).filter_by(ip=ip).update({Cmdb_acc_info.result: '0'})
                session.commit()
                session.close()
            else:
                pass



'''
====================================================================
03、将存活且密码不正确的机器尝试用户名密码
====================================================================
'''

def try_password(network_segment):
    username_lists = ['localadmin', 'root']
    password_lists = ['3a+GaV=#', '123456', '#1-9%az&', '&+eM2j8q']
    for username in username_lists:
        for password in password_lists:
            write_hosts(username, password, network_segment)


def write_hosts(username, password, network_segment):
    echo_command = "echo '[all]' > try_password"
    os.system(echo_command)
    network_segment_like = "%" + network_segment + "%"

    acc_infos = session.query(Cmdb_acc_info).filter_by(host_status='on').filter_by(result='0').filter(Cmdb_acc_info.ip.like(network_segment_like))
    print acc_infos
    host_info = acc_infos.first()
    print host_info.ip
    if host_info:
        for acc_info in acc_infos:
            ip = acc_info.ip
            print ip
            ansible_info = ip + " ansible_ssh_user=" + username + " ansible_ssh_pass='" + password + "' ansible_sudo_pass='" + password + "'\n"
            with open('try_password', "a+") as f:
                f.write(ansible_info)
        ansible_try_password(username, password)
    else:
        pass

def ansible_try_password(username, password):
    print "username: " + username
    print "password: " + password
    ansible = "ansible -i try_password all -m shell -a 'hostname' -f 80 -o"
    infos = os.popen(ansible)
    results = infos.readlines()

    for info in results:
        ip_re = re.compile(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])')
        result_re = re.compile(r'(.*SUCCESS.*)')
        ips = result_re.findall(info)
        if ips:
            sucess_reult = ips[0]
            sucess_ip = ip_re.findall(sucess_reult)
            ip = sucess_ip[0]
            print ip
            if ip:
                session.query(Cmdb_acc_info).filter_by(ip=ip).update(
                    {Cmdb_acc_info.username: username, Cmdb_acc_info.password: password, Cmdb_acc_info.result: '1'})
                session.commit()
                session.close()
            else:
                pass



'''
====================================================================
04、获取密码正确,且主机信息不存在的主机信息
====================================================================
'''

def get_asset_info(network_segment):
    asset_infos = session.query(Cmdb_hostbase).filter_by(hostname='').filter_by(host_status='on').join(Cmdb_acc_info, Cmdb_hostbase.ip == Cmdb_acc_info.ip).add_columns(Cmdb_acc_info.username, Cmdb_acc_info.password, Cmdb_acc_info.ip, Cmdb_acc_info.result, Cmdb_hostbase.ip).filter_by(result='1')
    # asset_infos = session.query(Cmdb_hostbase).filter_by(host_status='on').join(Cmdb_acc_info,
    #                                                                                                    Cmdb_hostbase.ip == Cmdb_acc_info.ip).add_columns(
    #     Cmdb_acc_info.username, Cmdb_acc_info.password, Cmdb_acc_info.ip, Cmdb_acc_info.result,
    #     Cmdb_hostbase.ip).filter_by(result='1')
    print asset_infos
    filename = network_segment + "hosts"
    echo_command = "echo '[all]' > %s" % filename
    os.system(echo_command)
    print filename
    for asset_info in asset_infos:
        ip = asset_info.ip
        username = asset_info.username
        password = asset_info.password
        ansible_info = ip + " ansible_ssh_user=" + username + " ansible_ssh_pass='" + password + "' ansible_sudo_pass='" + password + "'\n"
        with open(filename, "a+") as f:
            f.write(ansible_info)
        #执行获取信息的Python脚本
    ansible_get_info(filename)


def ansible_get_info(host_path):

    Options = namedtuple('Options',
                         ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check'])
    variable_manager = VariableManager()
    loader = DataLoader()
    options = Options(connection='ssh', module_path='/Library/Python/2.7/site-packages/ansible', forks=100, become=None,
                      become_method=None, become_user=None, check=False)
    passwords = dict(vault_pass='secret')

    results_callback = ResultCallback()

    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=host_path)
    # inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=['172.16.0.50', '172.16.0.190'])
    # variable_manager.extra_vars={"ansible_ssh_user":"root" , "ansible_ssh_pass":"3a+GaV=#"}

    variable_manager.set_inventory(inventory)

    play_source = dict(
        name="Ansible Play",
        hosts='all',
        gather_facts='no',
        tasks=[
            dict(action=dict(module='setup'), register='shell_out')
        ]
    )

    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            options=options,
            passwords=passwords,
            stdout_callback=results_callback,
        )
        tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()



def update_asset(asset_infos, ip):
    host_name = asset_infos[ip]['ansible_facts']['ansible_hostname']
    description = asset_infos[ip]['ansible_facts']['ansible_distribution']
    ansible_machine = asset_infos[ip]['ansible_facts']['ansible_distribution_version']
    sysinfo = '%s %s' % (description, ansible_machine)
    cpu_count = asset_infos[ip]['ansible_facts']['ansible_processor_count']
    mem_m = asset_infos[ip]['ansible_facts']['ansible_memtotal_mb']
    mem_g = int(round(float(mem_m) / float(1024)))
    ipadd_in = asset_infos[ip]['ansible_facts']['ansible_all_ipv4_addresses']
    # disk = results[ip]['ansible_facts']['ansible_devices']['vda']['size']
    data1 = asset_infos[ip]['ansible_facts']

    disk = sum([int(data1["ansible_devices"][i]["sectors"]) * \
                int(data1["ansible_devices"][i]["sectorsize"]) / 1024 / 1024 / 1024 \
                for i in data1["ansible_devices"] if i[0:2] in ("vd", "sr", "sd")])

    if len(ipadd_in) > 1:
        for ipv4 in ipadd_in:
            session.query(Cmdb_hostbase).filter_by(ip=ipv4).update({Cmdb_hostbase.hostname: host_name, \
                                                                    Cmdb_hostbase.ip: ipv4, \
                                                                    Cmdb_hostbase.cpu: cpu_count, \
                                                                    Cmdb_hostbase.memory: mem_g, \
                                                                    Cmdb_hostbase.disk: disk, \
                                                                    Cmdb_hostbase.machine_type: 'vm', \
                                                                    Cmdb_hostbase.os: sysinfo})
            session.commit()
            session.close()

    else:
        session.query(Cmdb_hostbase).filter_by(ip=ip).update({Cmdb_hostbase.hostname: host_name, \
                                                                Cmdb_hostbase.ip: ip, \
                                                                Cmdb_hostbase.cpu: cpu_count, \
                                                                Cmdb_hostbase.memory: mem_g, \
                                                                Cmdb_hostbase.disk: disk, \
                                                                Cmdb_hostbase.machine_type: 'vm', \
                                                                Cmdb_hostbase.os: sysinfo})
        session.commit()
        session.close()



if __name__ == '__main__':
    # network_segment = "172.16.0."
    segment_infos = session.query(Cmdb_net_segment_list).filter_by(status='U').all()
    session.close()
    for segment_ifo in segment_infos:
        network_segment = segment_ifo.segment

        # 01、判断ip是否存活,修改数据库状态
        ping_ip(network_segment)

        # 02、验证用户名密码
        verify_password(network_segment)

        # 03、将存活且密码不正确的机器尝试用户名密码
        try_password(network_segment)

        # 04、获取密码正确,且主机信息不存在的主机信息
        get_asset_info(network_segment)
