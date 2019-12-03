#! coding=utf-8
from mqtt.ssh_ssh import ssh_service
from conf.config_mqtt_uat import CONFIG_MQTT_UAT
from tqdm import tqdm
import time
import os
import re
import xlwt
import json
import operator

from mqtt.service import IN_DATA, BASE_DIR

hosts = CONFIG_MQTT_UAT.get('hostname').split(',')

env = "prod"  # "uat"


def ssh_sftp_service():
    for host in hosts:
        ssh_service(host)
        time.sleep(5)


def source_parse():
    date = CONFIG_MQTT_UAT.get("log_date")
    # for host_name in hosts:
    #     remote_date_name = "" if CONFIG_MQTT_UAT.get("log_date", "") == "" else ".{}".format(CONFIG_MQTT_UAT.get("log_date"))
    #     ip_in_data = '{}{}_in_data'.format(host_name, remote_date_name)
    #     source_path = os.path.join(BASE_DIR, "data/source", f"{host_name}/app.log{remote_date_name}")
    #     os.system(f'grep "\'message\': \'IC auth consumed time" {source_path} > ../{ip_in_data}')
    #     print(f"{host_name} 日志过滤完成。")
    #     time.sleep(2)
    # try:
    #     cmd = "bash " + os.path.join(BASE_DIR, "data/source", f'source_parse.sh {date}')
    #     os.system(cmd)
    # except Exception as e:
    #     print("目前还没有从服务器下载相应的log文件！请手动下载")
    #
    # print("原数据整理完成!")
    pass


class Business(object):

    def __init__(self):
        self._headers = {"log_time": "日志时间", "IP": "所属服务器IP", 'lock_id': "门锁ID", 'serial': "串号", 'card_id': "卡ID",
                         'card_type': "卡类型", 'time': "总用时(毫秒)"}
        self._data = self.files2list()
        self._card_type = {"17": "保洁卡", "18": "临时楼层卡", "20": "维修卡"}

    def files2list(self):
        k_v_list = []
        remote_date_name = "" if CONFIG_MQTT_UAT.get("log_date", "") == "" else ".{}".format(
            CONFIG_MQTT_UAT.get("log_date"))
        for h in hosts:
            file = os.path.join(os.path.join(IN_DATA, f'{h}{remote_date_name}_in_data'))
            with open(file, 'r') as f:
                for line in f:
                    if "IC auth consumed time" in line:
                        log_time = line[:23]
                        values = [log_time, h]
                        values.extend(re.compile(r'[lock_id|serial|card_id|card_type|time]:(\d*)', re.I).findall(line))
                        values[-1] = int(values[-1])
                        k_v_list.append(dict(zip(self._headers.keys(), values)))
        return sorted(k_v_list, key=lambda x: int(x['time']), reverse=True)

    @property
    def _execl_name(self):
        if CONFIG_MQTT_UAT.get("log_date") == "":
            # 获得当前时间时间戳
            now = int(time.time())
            # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
            timeStruct = time.localtime(now)
            return time.strftime("%Y-%m-%d", timeStruct)
        else:
            return CONFIG_MQTT_UAT.get("log_date")

    def to_execl(self):
        wk = xlwt.Workbook()
        sheet_one = wk.add_sheet("mqtt日志时间整理", cell_overwrite_ok=True)
        # 写标题
        for col_index, col_name in enumerate(self._headers.values()):
            sheet_one.write(0, col_index, col_name)
        for index, row in enumerate(self._data):  # 行
            for col, k in enumerate(self._headers.keys()):  # 列
                if k == "card_type":
                    content = "{}_{}".format(self._card_type.get(str(row[k]), "未知"), row[k])
                else:
                    content = row[k]
                sheet_one.write(index + 1, col, content)

        execl_name = "{}_mqtt_log_union.xls".format(self._execl_name)
        excel_file = os.path.join(IN_DATA, f'execls/{execl_name}')
        wk.save(excel_file)


if __name__ == "__main__":
    if env == "uat":
        ssh_sftp_service()
        print("获取有效文件完成!")
        time.sleep(3)

    if env == "prod":
        source_parse()
    b = Business()
    b.to_execl()
    print('数据收集完成！')
