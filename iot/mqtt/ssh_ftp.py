#! coding=utf-8
import os
import paramiko
from conf.config_mqtt_uat import CONFIG_MQTT_UAT
from mqtt.service import IN_DATA
import time


class SftpConf:
    host_name = CONFIG_MQTT_UAT.get('host_name')
    port = int(CONFIG_MQTT_UAT.get('port'))


sftp_conf = SftpConf()


class SshFtp(object):
    def __init__(self, host):
        self._trans = paramiko.Transport(
            sock=(host, sftp_conf.port)
        )
        self._trans.connect(
            username=CONFIG_MQTT_UAT.get('username'),
            password=CONFIG_MQTT_UAT.get("password")
        )
        self._sftp = paramiko.SFTPClient.from_transport(self._trans)

    def __del__(self):
        self._sftp.close()

    def upload(self, local_path_file, remote_path_file):
        # 上传
        # 把本地的文件settings.py，上传到远端为/root/Desktop/settings.py
        # self._sftp.put("settings.py", "/root/Desktop/settings.py")
        self._sftp.put(local_path_file, remote_path_file)

    def download(self, remote_path_file, local_path_file):
        self._sftp.get(remote_path_file, local_path_file)
        # 下载
        # 从远程/root/Desktop/hh.py获取文件下载到本地名称为hh.py
        # sftp.get("/root/Desktop/hh.py","hh.py")


def sftp_service(filename, host_name):
    sftp = SshFtp(host_name)
    local_path_file = os.path.join(IN_DATA, filename)
    sftp.download(f'/home/develop/{filename}', local_path_file)
    print(f'{filename} download finished!')
    time.sleep(2)
    sftp.__del__()

