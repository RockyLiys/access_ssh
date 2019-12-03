#! coding=utf-8

import paramiko
from conf.config_mqtt_uat import CONFIG_MQTT_UAT
from mqtt.service import *
from mqtt.ssh_ftp import *


class SSH(object):
    def __init__(self, host_name):
        self.c = paramiko.SSHClient()
        self.c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.c.connect(
            host_name,
            CONFIG_MQTT_UAT.get('port'),
            CONFIG_MQTT_UAT.get('username'),
            CONFIG_MQTT_UAT.get('password'),
            timeout=20
        )

    def __del__(self):
        self.c.close()

    def exec_cmd(self, command, print2=False):
        stdin, stdout, stderr = self.c.exec_command(command)
        return stdout.readlines()


def ssh_service(host_name):
    c = SSH(host_name)
    remote_date_name = "" if CONFIG_MQTT_UAT.get("log_date", "") == "" else ".{}".format(CONFIG_MQTT_UAT.get("log_date"))
    ip_in_data = '{}{}_in_data'.format(host_name, remote_date_name)

    server_ret = c.exec_cmd(f'ls ~/{ip_in_data}')
    if server_ret:
        c.exec_cmd('')
    else:
        c.exec_cmd(
            f'grep "\'message\': \'IC auth consumed time" /data/logs/backend.iot-mqtt-dispatch-service/app.log{remote_date_name} > ~/{ip_in_data}')
        sftp_service(ip_in_data, host_name)
        c.exec_cmd(f'rm -rf /home/develop/{ip_in_data}')

    c.__del__()


