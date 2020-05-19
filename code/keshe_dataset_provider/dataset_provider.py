# coding:utf-8

######################################
# 功能：模拟外界采集器输入测试集数据
# 输入：本地csv文件
# 处理：用json封装csv文件
# 输出：发送到指定地址的json信息

# 本代码仅仅发送一次数据，尚不支持持续发送
######################################


import os, json
import re
import requests
import pandas as pd
import numpy as np
import logging

# 设置日志格式，等级等
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "  # 配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a '  # 配置输出时间的格式，注意月份和天数不要搞乱了
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    filename=r"dataset_provider.log"  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                    )


class dataset_provider:
    def __init__(self, url_delete, url_save, db_save):

        self.pathlist = []
        self.namelist = []
        self.dataset = []
        self.url_delete = url_delete
        self.url_save = url_save
        self.db_save = db_save

    # 通过phm平台获取数据
    def get_dataset_from_phm_platform(self):
        url = 'https://api.phmlearn.com/component/data/zhoucheng'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        id_list = [100, 108, 121, 133, 147, 160, 172, 188, 200, 212, 225, 237, 249, 261] # 数据集编号
        atrribute_list = ['DE_time', 'FE_time', 'RPM']
        request_dict = {}
        request_dict['access_token'] = 'xxxxxxxx'
        for id in id_list:
            dict_ = {}
            length = 0  # 记录总长度
            for atrribute in atrribute_list:
                request_dict['divice_id'] = id
                request_dict['atrribute'] = atrribute
                try:
                    result = requests.post(url, headers=headers, params=request_dict)  # 发送数据
                    print(result)
                    if atrribute == 'RPM':  # RPM只有一行，所以要延长
                        dict_[atrribute] = np.ones(length) * result.json()['data']['data']
                        print(dict_[atrribute])
                    else:
                        dict_[atrribute] = result.json()['data']['data']
                        length = len(dict_[atrribute])
                    print(len(dict_[atrribute]))
                except Exception as e:
                    logging.error('failed to transport data')
                    break
            df = pd.DataFrame(dict_)
            print(df)
            Id = 'TEST' + str(id)
            self.send_dataset(df, Id)

    def get_dataset_name(self):
        # 获取数据集文件名
        for root, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if os.path.splitext(file)[1] == '.csv':
                    self.pathlist.append(os.path.join(root, file))
                    self.namelist.append(file)
        print(self.pathlist)
        logging.debug('dataset filename: %s', str(self.pathlist))

    def read_dataset(self):
        # 读取数据集
        for seq in range(len(self.pathlist)):
            self.send_dataset(pd.read_csv(self.pathlist[seq]), self.namelist[seq])

    # 删除数据库
    def delete_data(self):
        request_dict = {}
        request_dict['database'] = self.db_save
        request_dict = json.dumps(request_dict, ensure_ascii=False)
        headers = {'Content-Type': 'application/json'}
        result = requests.get(self.url_delete, headers=headers,
                              data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
        print(str(result.json()['msg']))

    # 发送数据，输入为数据和文件名，文件名将作为表名
    def send_dataset(self, data, filename):
        request_dict = {}
        request_dict['data'] = data.to_json(orient="split", force_ascii=False)

        seq = 1
        if request_dict['data']:
            request_dict['save_option'] = 'mongodb'
            request_dict['save_name'] = re.sub('.csv', '', filename)  # 设备名
            request_dict['data_type'] = 'Dataframe'
            request_dict['database'] = self.db_save
            # request_dict['transmit_to'] = 'directory'
            headers = {'Content-Type': 'application/json'}
            try:
                requests.post(self.url_save, headers=headers, data=json.dumps(request_dict, ensure_ascii=False))  # 发送数据
            except Exception as e:
                logging.error('failed to transport data')
            seq += 1

    def run(self, option):
        self.delete_data()
        if option == 0:  # 从本地获取数据
            self.get_dataset_name()
            self.read_dataset()
            logging.debug('transport finished')
        elif option == 1:  # 从phm平台获取数据
            self.get_dataset_from_phm_platform()
            logging.debug('transport finished')


def main():
    # 定义服务器ip地址和端口号
    ip = 'xxx.xxx.xxx.xxx'
    port = '5000'

    url_delete = 'http://%s:%s/keshe_middle_platform/api/v1/delete' % (ip, port)
    url_save = 'http://%s:%s/keshe_middle_platform/api/v1/save' % (ip, port)
    db_save = 'keshe_dataset'

    app = dataset_provider(url_delete, url_save, db_save)
    app.run(0)  # 输入为0则调取本地csv文件，输入为1则从phm平台调取数据


if __name__ == '__main__':
    main()

