# coding:utf-8

######################################
# 功能：用随机森林模型对测试集进行分类判断
# 输入：服务器端提供的测试集特征表
# 处理：用模型进行分类判断
# 输出：本地保存一个result.csv文件作为判断结果，同时将判断结果上传至服务器端供前端微信小程序调用

# 最终得分 准确率 精确率 召回率分别是： 89.02 96.48 90.82 88.04
######################################

from sklearn.externals import joblib
import json, time
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
                    filename=r"test.log"  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                    )

class Test:
    def __init__(self):
        self.params = {}
        self.params['model_directory'] = 'model/cwru.model'

    # 测试
    def test(self, df_dict):
        return_dict = {}
        for name in df_dict:
            data = df_dict[name]
            result = []
            # 读取模型
            clf = joblib.load(self.params['model_directory'])
            # 读取数据
            train_X = data.iloc[:, :data.shape[1] - 1]
            div = data.iloc[:, data.shape[1] - 1]  # 划分不同来源的数据，给数据分组
            div = np.array(div)

            # 进行预测
            train_Y = clf.predict(train_X)

            # 输出预测结果
            data_save = pd.DataFrame(columns=['label', 'filename'])

            cnt = 0
            N = 0
            a = []
            for i in range(div.shape[0]):  # 每一个测试集
                if not cnt:
                    N = div[cnt]
                if cnt:
                    if div[cnt] != N:
                        result.append(np.argmax(np.bincount(a)))  # 求出现次数最多的值
                        print('第%d组（%s）：' % (cnt, div[cnt - 1]), a)
                        print('测试结果：', result)
                        a = []
                        N = div[cnt]

                if train_Y[cnt] == 'normal':
                    a.append(0)
                elif train_Y[cnt] == 'ball':
                    a.append(1)
                elif train_Y[cnt] == 'outer race':
                    a.append(2)
                elif train_Y[cnt] == 'inner race':
                    a.append(3)

                # data_save.append([a[len(a)-1], names[div[cnt - 1] - 29]])
                data_save.loc[len(data_save)] = [a[len(a) - 1], div[cnt]]

                cnt += 1

            # 保存测试结果
            feature_normal = pd.DataFrame(data_save, columns=['label', 'filename'])
            feature_normal.to_csv('result_%s.csv' % str(time.strftime("%Y%m%d%H%M%S")), index=False)
            print(data_save.to_json(orient="split", force_ascii=False))
            return_dict[name]=feature_normal
            # 返回结果
        return return_dict


class LocalApi:
    # 输入参数为：上传url，下载url，自定义查询语句
    def __init__(self, url_delete, url_load, url_save, db_load, db_save):
        self.url_delete = url_delete # 删库url，每次重启程序时需要把上一次运行的结果删除，以免对结果造成干扰
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
        print(result)

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
                clist = clist.replace("'", '"').replace("true", "True").replace("false", "False").replace("None",
                                                                                                          "null")
                json_data_dict = json.loads(clist)  # 输出原本为一个只有一个元素的列表，唯一的元素是一个字典，所以此处json_data_dict为一个字典
                json_data_dict = json_data_dict['data']
                # 将json文件转化为Dataframe格式
                return_df = pd.DataFrame(json_data_dict['data'], columns=json_data_dict['columns'],
                                         index=json_data_dict['index'])
                return_dict[table] = return_df
        return return_dict

    # 根据字典上传数据
    def upload_data(self, return_df_dict):
        for i in return_df_dict:
            print(i)
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
                ans = Test()
                return_df_dict = ans.test(df_dict)
                # 处理完成...
                self.upload_data(return_df_dict)  # 上传处理结果
            time.sleep(5)

def main():
    # 定义服务器ip地址和端口号
    ip = 'xxx.xxx.xxx.xxx'
    port = '5000'

    url_delete = 'http://%s:%s/keshe_middle_platform/api/v1/delete' % (ip, port)
    url_load = 'http://%s:%s/keshe_middle_platform/api/v1/load' % (ip, port)
    url_save = 'http://%s:%s/keshe_middle_platform/api/v1/save' % (ip, port)

    db_load = 'keshe_featureset_aggregate'
    db_save = 'keshe_result'
    app = LocalApi(url_delete, url_load, url_save, db_load, db_save)
    app.run()

if __name__ == '__main__':
    main()
