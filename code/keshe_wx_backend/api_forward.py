# 使用imlbearn库中上采样方法中的SMOTE接口
from sklearn.ensemble import IsolationForest
import os, sys, json, time
from flask import Flask, request, jsonify, send_file
import requests
import pandas as pd
import numpy as np
import logging
import re

# 设置日志格式，等级等
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "  # 配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a '  # 配置输出时间的格式，注意月份和天数不要搞乱了
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    filename=r"api_forward.log"  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                    )

#向后查数据的api
class ApiBackward:
    # 输入参数为：上传url，下载url，自定义查询语句
    # option=1时进行数据库初始化
    def __init__(self, url_load, url_save, db_load, db_save):
        self.url_load = url_load  # 下载url
        self.url_save = url_save  # 上传url
        self.collist = []         # 已处理的表名
        self.db_load = db_load    # 读取数据库名
        self.db_save = db_save    # 保存数据库名

    # 获取表名, option=0时不断刷新
    def data_detect(self, option, db_load):
        request_dict = {}
        request_dict['database'] = db_load
        request_dict['database_check'] = 'yes'
        request_dict['request'] = ''
        request_dict['request_order'] = ''
        request_dict = json.dumps(request_dict, ensure_ascii=False)
        headers = {'Content-Type': 'application/json'}
        result = requests.get(self.url_load, headers=headers, data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
        clist = result.json()['data']  # 获得list类型的表名列表

        if option == 0: # 检查是否有新数据出现,返回新增表名列表
            new_col = []
            for col in clist:
                if col not in self.collist:
                    self.collist.append(col)
                    new_col.append(col)
            return new_col
        else:  #返回所选数据库下的所有表名
            return clist

    # 下载数据，输入表名列表（new_col）和数据库名，返回两个字典，内容为{表名：数据dataframe}
    def download_data(self, new_col, db_load):
        return_dict = {}
        time_dict = {}
        for table in new_col:
            request_dict = {}
            request_dict['database'] = db_load
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
                time_dict[table] = json_data_dict['time'] # 打上时间标签
                json_data_dict = json_data_dict['data']
                # 将json文件转化为Dataframe格式
                return_df = pd.DataFrame(json_data_dict['data'], columns=json_data_dict['columns'],
                                         index=json_data_dict['index'])
                return_dict[table] = return_df
        return return_dict, time_dict

    # 根据字典上传数据
    def upload_data(self, return_df_dict, db_save):
        for i in return_df_dict:
            request_dict = {}
            request_dict['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            request_dict['data'] = return_df_dict[i].to_json(orient="split", force_ascii=False)
            if request_dict['data']:
                request_dict['database'] = db_save
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

    #################数据库初始化函数#################


    # 主界面-事件数据获取
    # 返回一张事件信息表，表中每条信息包含：故障索引, 故障机组名，故障时间段，故障类型
    def main_event_data(self):
        db_load = 'keshe_result'
        col = self.data_detect(1, db_load)
        df_dict, time_dict = self.download_data(col, db_load)
        #数据处理
        event_machine = []
        event_time = []
        event_err_type = []
        event_index = []
        machine_index = []
        for i in df_dict:
            df_machine = df_dict[i].iloc[:, 1]
            df_err_type = df_dict[i].iloc[:, 0]
            for j in range(len(df_err_type)): #遍历所有行
                if df_err_type[j]!=0:
                    event_machine.append(df_machine[j])
                    event_err_type.append(df_err_type[j])
                    event_time.append(time_dict[i])
                    event_index.append(j)
                    machine_index.append(int(re.search('\d+', df_machine[j - 1]).group()))  # 获取设备名对应的数字（设备名必须包含数字）

        #保存
        event_index = np.array(event_index)
        event_index.reshape((len(event_index), 1))
        event_machine = np.array(event_machine)
        event_machine.reshape((len(event_machine), 1))
        event_time = np.array(event_time)
        event_time.reshape((len(event_time), 1))
        event_err_type = np.array(event_err_type)
        event_err_type.reshape((len(event_err_type), 1))
        machine_index = np.array(machine_index)
        machine_index.reshape((len(machine_index), 1))

        event_index = pd.DataFrame(event_index, columns=['index'])
        event_machine = pd.DataFrame(event_machine, columns=['machine'])
        event_time = pd.DataFrame(event_time, columns=['time'])
        event_err_type = pd.DataFrame(event_err_type, columns=['err_type'])
        machine_index = pd.DataFrame(machine_index, columns=['machine_index'])

        event_df = pd.concat([event_index, event_machine, event_time, event_err_type, machine_index], axis=1)

        return event_df

    # 主界面-机组 数据获取
    # 返回一个状态信息列表，表中每个元素对应每台机器的状态，状态包括：无数据，无故障，三种不同的故障类型
    def main_machine_data(self):
        db_load = 'keshe_result'
        col = self.data_detect(1, db_load)
        df_dict, time_dict = self.download_data(col, db_load)  #从数据库获取数据
        # 数据处理
        event_machine = []
        event_err_type = []
        machine_index = []
        for i in df_dict:
            df_machine = df_dict[i].iloc[:, 1]
            df_err_type = df_dict[i].iloc[:, 0]

            #遍历全表，找出最新的判断结果
            last_name = ''
            for j in range(len(df_err_type)):
                if j == 0:
                    last_name = df_machine[j]
                elif df_machine[j] != last_name:
                    event_machine.append(df_machine[j-1])
                    event_err_type.append(df_err_type[j-1])
                    machine_index.append(int(re.search('\d+', df_machine[j-1]).group()))  #获取设备名对应的数字（设备名必须包含数字）
                    last_name = df_machine[j]


        # 保存(转换成数组然后转置）
        event_machine = np.array(event_machine)
        event_machine.reshape((len(event_machine), 1))
        event_err_type = np.array(event_err_type)
        event_err_type.reshape((len(event_err_type), 1))
        machine_index = np.array(machine_index)
        machine_index.reshape((len(machine_index), 1))

        event_machine = pd.DataFrame(event_machine, columns=['machine'])
        event_err_type = pd.DataFrame(event_err_type, columns=['err_type'])
        machine_index = pd.DataFrame(machine_index, columns=['machine_index'])

        # 此处event_list字典的值会作为表名
        event_df = pd.concat([event_machine, event_err_type, machine_index], axis=1)

        print(event_df)

        return event_df

    # 机组界面数据获取
    # 查询单个机组的数据，返回监控数据，特征数据和历史故障记录
    # 机组名即为表名
    def machine_data(self, machine_seq):
        db_load1 = 'keshe_dataset'      # 查询监控数据
        db_load2 = 'keshe_featureset'   # 查询特征数据
        db_load3 = 'keshe_result'         # 查询历史故障记录

        #根据machine_seq获取machine_name
        machine_name = 'TEST' + str(machine_seq)
        print(machine_name)

        # 获取数据
        col = []
        col.append(machine_name)
        df_dict1, time_dict1 = self.download_data(col, db_load1)  #监控数据
        df_dict2, time_dict2 = self.download_data(col, db_load2)  #特征数据
        col = []
        col.append('test')
        df_dict3, time_dict3 = self.download_data(col, db_load3)  #历史故障记录

        # 故障记录处理
        event_time = []
        event_err_type = []
        event_index = []
        for i in df_dict3:
            df_machine = df_dict3[i].iloc[:, 1]
            df_err_type = df_dict3[i].iloc[:, 0]
            for j in range(len(df_err_type)):
                if df_machine[j] == machine_name:
                    event_err_type.append(df_err_type[j])
                    event_time.append(time_dict3[i])
                    event_index.append(j)

        # 保存
        event_index = np.array(event_index)
        event_index.reshape((len(event_index), 1))
        event_time = np.array(event_time)
        event_time.reshape((len(event_time), 1))
        event_err_type = np.array(event_err_type)
        event_err_type.reshape((len(event_err_type), 1))

        event_index = pd.DataFrame(event_index, columns=['index'])
        event_time = pd.DataFrame(event_time, columns=['time'])
        event_err_type = pd.DataFrame(event_err_type, columns=['err_type'])

        event_df = pd.concat([event_index, event_time, event_err_type], axis=1)

        # 控制长度
        # 此处的len(df_dict2[machine_name])即为行数
        while len(df_dict1[machine_name]) > 100:
            df_dict1[machine_name] = df_dict1[machine_name].iloc[10:,:]
        while len(df_dict2[machine_name]) > 50:
            df_dict2[machine_name] = df_dict2[machine_name].iloc[5:,:]

        return df_dict1[machine_name], df_dict2[machine_name], event_df

    # 机组界面历史监控数据下载
    def machine_history_origin_data(self, machine_seq):

        # 根据machine_seq获取machine_name
        machine_name = 'TEST' + str(machine_seq)
        print("downloading machine history origin data:", machine_name)

        # 获取数据
        db_load = 'keshe_dataset'  # 查询监控数据
        col = []
        col.append(machine_name)
        df_dict, time_dict = self.download_data(col, db_load)  # 从后端数据库获取数据

        #将结果保存在csv文件中，api直接将csv文件发送到用户端
        feature_normal = pd.DataFrame(df_dict[machine_name])
        feature_normal.to_csv('machine_history_origin.csv', index=False)

    # 机组界面历史特征数据下载
    def machine_history_feature_data(self, machine_seq):

        # 根据machine_seq获取machine_name
        machine_name = 'TEST' + str(machine_seq)
        print("downloading machine history feature data:", machine_name)

        # 获取数据
        db_load = 'keshe_featureset'  # 查询监控数据
        col = []
        col.append(machine_name)
        df_dict, time_dict = self.download_data(col, db_load)  # 从后端数据库获取数据

        # 将结果保存在csv文件中，api直接将csv文件发送到用户端
        feature_normal = pd.DataFrame(df_dict[machine_name])
        feature_normal.to_csv('machine_history_feature.csv', index=False)

    # 事件界面数据获取
    # 查询单次故障的记录，返回单个时间窗口内的监控数据和单个时间窗口内的特征数据
    # event_index为result库test表中对应的序号, len_piece为时间窗口大小
    def event_data(self, event_index, len_piece):
        db_load1 = 'keshe_dataset'  # 查询监控数据
        db_load2 = 'keshe_featureset_aggregate'  # 查询特征数据
        relative_index = 0 #原始数据在数据表中的位置

        # 获取数据
        col = []
        col.append('test') #特征数据的表名为test
        df_dict2, time_dict2 = self.download_data(col, db_load2)  # 得到特征数据行

        df = df_dict2['test']
        machine_name = df.iloc[event_index, df.shape[1]-1]  # 获取设备名
        feature = df.iloc[event_index, :df.shape[1]-1]      # 获取特征字段

        col = []
        col.append(machine_name)  # 特征数据的表名为test
        df_dict1, time_dict1 = self.download_data(col, db_load1)  # 根据设备名获取监控数据

        seq = 1
        while df.iloc[event_index - seq, df.shape[1] - 1] == machine_name:  # 原始数据在数据表中的位置（因为原始数据表不是一张表）
            relative_index += 1
            seq += 1

        df = df_dict1[machine_name]
        dataset = df.iloc[relative_index*len_piece:(relative_index+1)*len_piece, :df.shape[0] - 1]  # 获取对应的监控数据

        # 控制长度
        # 此处的len(df_dict2[machine_name])即为行数
        while len(dataset) > 100:
            dataset = dataset.iloc[10:, :]

        return dataset, feature

    # 事件界面历史监控数据下载
    def event_history_origin_data(self, event_index, len_piece):
        db_load1 = 'keshe_dataset'  # 查询监控数据
        db_load2 = 'keshe_featureset_aggregate'  # 查询特征数据
        relative_index = 0  # 原始数据在数据表中的位置

        # 获取数据
        col = []
        col.append('test')  # 特征数据的表名为test
        df_dict2, time_dict2 = self.download_data(col, db_load2)  # 得到特征数据行

        df = df_dict2['test']
        machine_name = df.iloc[event_index, df.shape[1] - 1]  # 获取设备名

        col = []
        col.append(machine_name)  # 特征数据的表名为test
        df_dict1, time_dict1 = self.download_data(col, db_load1)  # 根据设备名获取监控数据

        seq = 1
        while df.iloc[event_index - seq, df.shape[1] - 1] == machine_name:  # 原始数据在数据表中的位置（因为原始数据表不是一张表）
            relative_index += 1
            seq += 1

        df = df_dict1[machine_name]
        dataset = df.iloc[relative_index * len_piece:(relative_index+1) * len_piece, :df.shape[0] - 1]  # 获取对应的监控数据

        # 控制长度
        # 此处的len(df_dict2[machine_name])即为行数
        while len(dataset) > 100:
            dataset = dataset.iloc[10:, :]

        # 将结果保存在csv文件中，api直接将csv文件发送到用户端
        dataset.to_csv('event_history_origin.csv', index=False)
        return dataset

    # 事件界面历史特征数据下载
    def event_history_feature_data(self, event_index):
        db_load2 = 'keshe_featureset_aggregate'  # 查询特征数据

        # 获取数据
        col = []
        col.append('test')  # 特征数据的表名为test
        df_dict2, time_dict2 = self.download_data(col, db_load2)  # 得到特征数据行

        df = df_dict2['test']
        feature = df.iloc[event_index, :df.shape[1] - 1]  # 获取特征字段

        # 将结果保存在csv文件中，api直接将csv文件发送到用户端
        #feature = pd.DataFrame(feature, columns=[feature.iloc[:, 0]])

        dict_feature = {'feature': feature.index, 'data': feature.values}
        feature = pd.DataFrame(dict_feature)
        feature.to_csv('event_history_feature.csv', index=False)
        return feature




#向前发数据的api
class ApiForward:
    # 输入参数为：上传url，下载url，自定义查询语句
    # 准备好前端所用的数据库
    def __init__(self, url_load, url_save):
        self.url_load = url_load  # 下载url
        self.url_save = url_save  # 上传url

    def get_df(self, db_name):
        pass

    #################初始化函数#################

    # 生成主界面-事件数据表
    # 函数的详细说明见ApiBackward类
    def main_event(self):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        return a.main_event_data()
    def main_machine(self):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        return a.main_machine_data()
    def machine(self, machine_seq):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        return a.machine_data(machine_seq)
    def machine_history_origin(self, machine_seq):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        a.machine_history_origin_data(machine_seq)
    def machine_history_feature(self, machine_seq):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        a.machine_history_feature_data(machine_seq)
    def event(self, event_index, len_piece):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        return a.event_data(event_index, len_piece)
    def event_history_origin(self, event_index, len_piece):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        a.event_history_origin_data(event_index, len_piece)
    def event_history_feature(self, event_index):
        a = ApiBackward(self.url_load, self.url_save, 'none', 'none')
        a.event_history_feature_data(event_index)

    def run(self):
        app = Flask(__name__)
        WX_URL = '/keshe/api/v1/'

        #################小程序请求数据#################

        # 主界面-事件数据获取
        # 返回一张事件信息表，表中每条信息包含：故障机组名，故障时间段，故障类型
        @app.route(WX_URL + 'main/event', methods=['GET'])
        def main_event_data():
            return_dict = {'status': 0, 'msg': 'null', 'data': 'null', 'success': 'false'}
            table1 = self.main_event()
            return_dict['data'] = table1.to_json(orient="split", force_ascii=False)
            return_dict['success'] = 'true'
            return jsonify(return_dict)

        # 主界面-机组 数据获取
        # 返回一个状态信息列表，表中每个元素对应每台机器的状态，状态包括：无数据，无故障，三种不同的故障类型
        @app.route(WX_URL + 'main/machine', methods=['GET'])
        def main_machine_data():
            return_dict = {'status': 0, 'msg': 'null', 'data': 'null', 'success': 'false'}
            table1 = self.main_machine()
            return_dict['data'] = table1.to_json(orient="split", force_ascii=False)
            return_dict['success'] = 'true'
            return jsonify(return_dict)


        # 机组界面数据获取
        # 查询单个机组的数据，返回监控数据，特征数据和历史故障记录
        @app.route(WX_URL + 'machine/data', methods=['GET'])
        def machine_data():
            return_dict = {'status': 0, 'msg': 'null', 'success': 'false'}
            # 获取表名
            get_data = request.args.to_dict()
            machine_seq = get_data.get('machine_seq')
            # 检查是否传参
            if not machine_seq:
                return_dict['msg'] = 'invalid input'
                return jsonify(return_dict)

            table1, table2, table3 = self.machine(machine_seq)
            return_dict['data_monitor'] = table1.to_json(orient="split", force_ascii=False)
            return_dict['data_feature'] = table2.to_json(orient="split", force_ascii=False)
            return_dict['data_error'] = table3.to_json(orient="split", force_ascii=False)
            return_dict['success'] = 'true'
            return jsonify(return_dict)


        # 机组界面历史监控数据下载
        @app.route(WX_URL + 'machine/history/origin_data', methods=['GET'])
        def machine_history_origin_data():
            return_dict = {'status': 0, 'msg': 'null', 'data': 'null', 'success': 'false'}
            # 获取表名
            get_data = request.args.to_dict()
            machine_seq = get_data.get('machine_seq')
            # 检查是否传参
            if not machine_seq:
                return_dict['msg'] = 'invalid input'
                return jsonify(return_dict)
            self.machine_history_origin(machine_seq)
            return send_file('machine_history_origin.csv',
                             mimetype='text/csv',
                             attachment_filename='machine_history_feature.csv',
                             as_attachment=True)

        # 机组界面历史特征数据下载
        @app.route(WX_URL + 'machine/history/feature_data', methods=['GET'])
        def machine_history_feature_data():
            return_dict = {'status': 0, 'msg': 'null', 'data': 'null', 'success': 'false'}
            # 获取表名
            get_data = request.args.to_dict()
            machine_seq = get_data.get('machine_seq')
            # 检查是否传参
            if not machine_seq:
                return_dict['msg'] = 'invalid input'
                return jsonify(return_dict)
            self.machine_history_feature(machine_seq)
            return send_file('machine_history_feature.csv',
                             mimetype='text/csv',
                             attachment_filename='machine_history_feature.csv',
                             as_attachment=True)

        # 事件界面数据获取
        # 查询单次故障的记录，返回单个时间窗口内的监控数据和单个时间窗口内的特征数据
        @app.route(WX_URL + 'event/data', methods=['GET'])
        def event_data():
            return_dict = {'status': 0, 'msg': 'null', 'success': 'false'}
            len_piece = 2000  #窗口大小，数值需与特征训练的窗口大小一致
            # 获取表名
            get_data = request.args.to_dict()
            event_index = int(get_data.get('event_index'))
            # 检查是否传参
            if not event_index:
                return_dict['msg'] = 'invalid input'
                return jsonify(return_dict)

            table1, table2 = self.event(event_index, len_piece)
            return_dict['dataset'] = table1.to_json(orient="split", force_ascii=False)
            return_dict['featureset'] = table2.to_json(orient="split", force_ascii=False)
            return_dict['success'] = 'true'
            return jsonify(return_dict)

        # 事件界面历史监控数据下载
        @app.route(WX_URL + 'event/history/origin_data', methods=['GET'])
        def event_history_origin_data():
            return_dict = {'status': 0, 'msg': 'null', 'success': 'false'}
            len_piece = 2000  # 窗口大小，数值需与特征训练的窗口大小一致
            # 获取表名
            get_data = request.args.to_dict()
            event_index = int(get_data.get('event_index'))
            # 检查是否传参
            if not event_index:
                return_dict['msg'] = 'invalid input'
                return jsonify(return_dict)

            self.event_history_origin(event_index, len_piece)
            return send_file('event_history_origin.csv',
                             mimetype='text/csv',
                             attachment_filename='event_history_origin.csv',
                             as_attachment=True)

        # 事件界面历史特征数据下载
        @app.route(WX_URL + 'event/history/feature_data', methods=['GET'])
        def event_history_feature_data():
            return_dict = {'status': 0, 'msg': 'null', 'success': 'false'}
            # 获取表名
            get_data = request.args.to_dict()
            event_index = int(get_data.get('event_index'))
            # 检查是否传参
            if not event_index:
                return_dict['msg'] = 'invalid input'
                return jsonify(return_dict)

            self.event_history_feature(event_index)
            return send_file('event_history_feature.csv',
                             mimetype='text/csv',
                             attachment_filename='event_history_feature.csv',
                             as_attachment=True)


        app.run(threaded=True, processes=True, host='0.0.0.0', port=5100, debug=True)


def main():
    url_load = 'http://47.108.65.135:5000/keshe_middle_platform/api/v1/load'
    url_save = 'http://47.108.65.135:5000/keshe_middle_platform/api/v1/save'
    app = ApiForward(url_load, url_save)
    app.run()


if __name__ == '__main__':
    main()
