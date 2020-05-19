# coding:utf-8

######################################
# 功能：将数据整合成单个文件，方便输出最终结果csv文件
# 输入：服务器提供的多张特征数据表
# 处理：整合所有特征数据表
# 输出：一张特征数据表，上传至服务器

# 按道理，如果要求数据实时更新的话，我不应该把所有数据都整合在一起。我可以对特征处理完成的数据直接进行分类，然后把结果追加到result.csv文件中。
# 不过我觉得一次性生成一个完整的csv文件可能更方便测试及展示，就保留了这部分代码。
######################################

import pandas as pd
import numpy as np
from sklearn.preprocessing import Imputer
import json, time
import requests
import logging

# 设置日志格式，等级等
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "  # 配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a '  # 配置输出时间的格式，注意月份和天数不要搞乱了
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    filename=r"aggregate.log"  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                    )

class Aggregate:
    def __init__(self):
        self.params = {}

    # 合并数据集
    def aggregate(self, df_dict):
        return_dict = {}

        # 数据整合成train_X，来源标记为train_Z
        seq = 1
        train_Y = []
        train_Z = []
        col = []

        for file in df_dict:
            print('开始合并:', file)
            # 读取文件
            data = df_dict[file]
            # 获取列名
            if not col:
                col = list(data)
                print(col)
            # 获取数据
            if seq == 1:
                train_X = pd.DataFrame(data)
            else:
                train_X = train_X.append(data)

            for i in range(data.shape[0]):
                train_Z.append(file)  # 添加标签

            seq += 1

        train_Z = np.array(train_Z)
        train_Z.reshape((len(train_Z), 1))

        # 使用均值填充空值
        imp_mean = Imputer(missing_values=np.nan, strategy='mean')
        imp_mean.fit(train_X)
        train_X = imp_mean.transform(train_X)

        # 将标签整合到新数据集中
        train_X = pd.DataFrame(train_X, columns=col)
        train_Z = pd.DataFrame(train_Z, columns=['label'])
        test_X = pd.concat([train_X, train_Z], axis=1)

        # 保存测试集
        testset = pd.DataFrame(test_X)
        return_dict['test'] = testset

        return return_dict

class LocalApi:
    # 输入参数为：上传url，下载url，自定义查询语句
    def __init__(self, url_delete, url_load, url_save, db_load, db_save):
        self.url_delete = url_delete
        self.url_load = url_load  # 下载url
        self.url_save = url_save  # 上传url
        self.collist = []  # 已处理的表名
        self.db_load = db_load
        self.db_save = db_save

    # 删除数据
    def delete_data(self):
        request_dict = {}
        request_dict['database'] = self.db_save
        request_dict = json.dumps(request_dict, ensure_ascii=False)
        headers = {'Content-Type': 'application/json'}
        result = requests.get(self.url_delete, headers=headers,
                              data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
        print(str(result.json()['msg']))

    # 检查是否有新数据出现,返回新增表名列表
    def data_detect(self):
        request_dict = {}
        request_dict['database'] = self.db_load
        request_dict['database_check'] = 'yes'
        request_dict['request'] = ''
        request_dict['request_order'] = ''
        request_dict = json.dumps(request_dict, ensure_ascii=False)
        headers = {'Content-Type': 'application/json'}
        result = requests.get(self.url_load, headers=headers, data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
        clist = result.json()['data']  # 获得list类型的表名列表

        new_col = []
        for col in clist:
            if col not in self.collist:
                self.collist.append(col)
                new_col.append(col)
        return new_col

    # 下载数据，返回一个字典，内容为{表名：数据dataframe}
    def download_data(self, new_col):
        return_dict = {}
        for table in new_col:
            request_dict = {}
            request_dict['database'] = self.db_load
            request_dict['database_check'] = ''
            request_dict['request'] = table
            request_dict['request_order'] = ''
            request_dict = json.dumps(request_dict, ensure_ascii=False)
            headers = {'Content-Type': 'application/json'}
            result = requests.get(self.url_load, headers=headers,
                                  data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
            clist = str(result.json()['data'])  # 获得数据表
            if clist:
                # 规范json格式
                clist = clist.replace("'", '"').replace("true", "True").replace("false", "False").replace("None","null")
                json_data_dict = json.loads(clist)  # 输此处json_data_dict为一个字典
                json_data_dict = json_data_dict['data']
                # 将json文件转化为Dataframe格式
                return_df = pd.DataFrame(json_data_dict['data'], columns=json_data_dict['columns'],
                                         index=json_data_dict['index'])
                return_dict[table] = return_df
        return return_dict

    # 根据字典上传数据
    def upload_data(self, return_df_dict):
        for i in return_df_dict:
            print('column %s save to %s'%(i, self.db_save))
            request_dict = {}
            request_dict['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            request_dict['data'] = return_df_dict[i].to_json(orient="split", force_ascii=False)
            print('==============')
            if request_dict['data']:
                request_dict['database'] = self.db_save
                request_dict['save_option'] = 'mongodb'
                request_dict['save_name'] = i
                request_dict['data_type'] = 'Dataframe'
                # request_dict['transmit_to'] = 'directory'
                headers = {'Content-Type': 'application/json'}
                try:
                    result = requests.post(self.url_save, headers=headers,
                                           data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
                    print('result=', result)
                except Exception as e:
                    print('transmit error:', e)
                    logging.error('transmit error:', e)

    def run(self):
        self.delete_data()
        while 1:
            print('checking')
            new_col = self.data_detect()  # 查询指定数据库下是都有新表生成
            if new_col:
                df_dict = self.download_data(new_col)  # 下载新表
                # 数据处理...
                aggr = Aggregate()
                return_df_dict = aggr.aggregate(df_dict)
                # 处理完成...
                self.upload_data(return_df_dict)  # 上传处理结果
            time.sleep(5)


def main():
    # 定义服务器ip地址和端口号
    ip = '47.108.65.135'
    port = '5000'

    url_delete = 'http://%s:%s/keshe_middle_platform/api/v1/delete' % (ip, port)
    url_load = 'http://47.108.65.135:5000/keshe_middle_platform/api/v1/load'
    url_save = 'http://47.108.65.135:5000/keshe_middle_platform/api/v1/save'
    db_load = 'keshe_featureset'
    db_save = 'keshe_featureset_aggregate'
    app = LocalApi(url_delete, url_load, url_save, db_load, db_save)
    app.run()


if __name__ == '__main__':
    main()






