# coding:utf-8

######################################
# 功能：接收json信息，并根据信息中的指令进行数据存取和转发

# 输入：监听收到的json信息
# 处理：根据其中的指令对数据库进行存取
# 输出：回复json信息

# json请求参数：
# instruction: list类型，代表指令，值包含：save(保存), load(读取), transmit(转发)
# asked_name: 请求数据的名称
# data: json封装的数据
#
######################################

import json, re, time
from flask import Flask, request
import pandas as pd
import numpy as np
from pymongo import MongoClient
import gridfs
import ast
import logging

# 设置日志格式，等级等
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "  # 配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a '  # 配置输出时间的格式，注意月份和天数不要搞乱了
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt=DATE_FORMAT,
                    filename=r"middle.log"  # 有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                    )


# 数据库操作
# 存储模式：gridfs
class DataBase:
    def __init__(self, db_name):
        # 设置登录IP，密码，数据库ip，数据库名
        usr = 'xxxxxxxx'
        passwd = 'xxxxxxxx'
        ip = 'xxx.xxx.xxx.xxx'
        # 建立连接
        self.db = MongoClient('mongodb://%s:%s@%s' % (usr, passwd, ip))[db_name]
        self.fs = gridfs.GridFS(self.db)
        self.db_name = db_name

    # 向表插入数据
    # 注意：data原本的格式必须是json格式
    def _insert(self, col_name, data):
        # 转换符号
        if data:
            data = data.replace("'", '"').replace("true", "True").replace("false", "False").replace("None", "null")

        order = '{"time": "%s", "data": %s}' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), str(data))

        order = order.encode('utf-8')  # 编码
        up = self.fs.put(data=order, filename=col_name)  # 上传
        print(up)
        print('inserted')

    # 请求数据
    def _query(self, col_name):
        print('query begin')
        print(col_name)
        print(self.db_name)

        down = self.fs.get_version(col_name).read()  # 下载

        down = json.loads(down.decode("utf-8").replace('None', 'null'), strict=False)  # 转化为json格式

        return down

    # 查询数据库，返回数据库中保存的所有数据名
    def _check(self):
        print('check begin')

        col_names = []

        # 提取所有文件名
        for grid_out in self.db['fs.files'].find({}, {"_id": 0, "filename": 1}):  # 数据库中的fs.files表存储了文件名信息
            col_names.append(grid_out['filename'])

        # 去除重复值
        return_list = []
        for d in col_names:
            if d not in return_list:
                return_list.append(d)

        print(return_list)
        return return_list

    # 删除数据库
    def _delete(self):
        self.db.command("dropDatabase")
        print('database %s deleted' % str(self.db_name))

    # 自定义数据库检索（格式转换可能转成dict，还存在bug）
    def _custom(self, col_name, _request_order):
        return_list = []
        _request_order = _request_order.replace("'", '"').replace("true", "True").replace("false", "False").replace(
            "Null", "none")
        _request_order = ast.literal_eval(_request_order)
        print(_request_order)
        print(type(_request_order))
        col = self.db[col_name]
        data = col.find(_request_order)
        for file in data:
            return_list.append(file)
        return return_list


# 接口集合
class Middle:
    def __init__(self):
        pass

    def save_to_database(self, db_name, col_name, data):
        DB = DataBase(db_name)
        DB._insert(col_name, data)

    def load_from_database(self, db_name, col_name):
        DB = DataBase(db_name)
        return_list = DB._query(col_name)
        return return_list

    def database_check(self, db_name):
        DB = DataBase(db_name)
        return_list = DB._check()
        return return_list

    def delete_database(self, db_name):
        DB = DataBase(db_name)
        DB._delete()

    def custom_database_check(self, db_name, col_name, _request_order):
        DB = DataBase(db_name)
        return_list = DB._custom(col_name, _request_order)
        return return_list

    def run(self):
        app = Flask(__name__)
        MY_URL = '/keshe_middle_platform/api/v1/'

        # 接收删库命令
        @app.route(MY_URL + 'delete', methods=['GET'])
        def delete():
            logging.debug('received database delete request')
            return_dict = {'status': 1, 'msg': 'null', 'data': 'null'}
            if request.args is None:
                return_dict['msg'] = '请求参数为空'
                return json.dumps(return_dict, ensure_ascii=False)

            json_data = request.get_json()  # 传入str类型的json_data
            json_data = ast.literal_eval(json_data)  # 将json_data改为dict类型

            db_name = json_data['database']  # 指定操作的数据库名

            self.delete_database(db_name)  # 删库

            return_dict['status'] = 0
            return_dict['msg'] = '数据库%s删除成功' % str(db_name)
            return json.dumps(return_dict, ensure_ascii=False)

        # 接收数据并存入数据库
        # 此处请求只接受json格式，url传参无效
        @app.route(MY_URL + 'save', methods=['POST'])
        def save():
            logging.debug('received post')
            return_dict = {'status': 1, 'msg': 'null', 'data': 'null'}
            # 判断参数是否为空
            if request.args is None:
                return_dict['msg'] = '请求参数为空'
                return json.dumps(return_dict, ensure_ascii=False)
            # 获取传入参数
            get_data = request.get_data()
            json_data = json.loads(get_data.decode("utf-8"), strict=False)  # 此时json_data格式为dict

            db_name = json_data['database']  # 指定操作的数据库名
            data = json_data['data']  # json格式的数据
            data_type = json_data['data_type']  # data原本的的数据类型
            save_option = json_data['save_option']  # 存储选项，可选为：mongodb，no
            save_name = json_data['save_name']  # 指定保存数据的表名
            # 将获取的数据存入数据库
            if save_option == 'mongodb':
                e = self.save_to_database(db_name, save_name, data)
                if e:
                    return_dict['msg'] = '函数运行出错: %s' % str(e)
                    return json.dumps(return_dict, ensure_ascii=False)
                return_dict['status'] = 0
                return json.dumps(return_dict, ensure_ascii=False)

        # 根据请求返回对应数据
        @app.route(MY_URL + 'load', methods=['GET'])
        def load():
            logging.debug('received get')
            return_dict = {'status': 1, 'msg': 'null', 'data': 'null'}
            # 判断参数是否为空
            if request.args is None:
                return_dict['msg'] = '请求参数为空'
                return json.dumps(return_dict, ensure_ascii=False)
            # 获取传入参数
            json_data = request.get_json()  # 传入str类型的json_data
            json_data = ast.literal_eval(json_data)  # 将json_data改为dict类型

            db_name = json_data['database']  # 指定操作的数据库名
            db_check = json_data['database_check']  # 查询数据库中的所有表名
            _request = json_data['request']  # 请求数据表名
            _request_order = json_data['request_order']  # 用户自定义查询语句，无查询时输入""

            # 请求数据库
            if _request_order:  # 用户自定义查询
                e = self.custom_database_check(db_name, _request, _request_order)
            elif db_check == 'yes':
                e = self.database_check(db_name)
            else:  # 返回请求的数据表
                e = self.load_from_database(db_name, _request)
            if e == 1:
                return_dict['msg'] = '函数运行出错: %s' % str(e)
                return json.dumps(return_dict, ensure_ascii=False)
            return_dict['data'] = e
            return_dict['status'] = 0
            return json.dumps(return_dict, ensure_ascii=False)

        app.run(threaded=True, processes=True, host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    app = Middle()
    app.run()
