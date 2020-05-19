# coding:utf-8

######################################
# 功能：进行特征提取
# 输入：服务器提供的原始数据
# 处理：提取特征
# 输出：特征提取结果，上传至服务器

# 经过测试，2600的窗口大小可以得到较好的结果

# 程序运行开始后会持续对服务器端进行间隔5秒的监听（屏幕输出"checking"），如果发现原始数据库中出现新的文件，就立刻获取这些文件。当程序运行完成时，
# 程序会一直间隔5秒输出”checking”，这时就可以关闭程序了

# 设置监听功能的初衷是让程序支持数据的实时更新，不过由于数据获取端不支持实时获取新数据，再加上我的开发能力有限，时间比较紧迫，我们的程序总体并未
# 实现实时更新数据的功能
######################################

import json, time
import pandas as pd
import numpy as np
from scipy import fftpack
import pywt
import requests
import logging

#设置日志格式，等级等
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s "#配置输出日志格式
DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a ' #配置输出时间的格式，注意月份和天数不要搞乱了
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt = DATE_FORMAT ,
                    filename=r"feature_get.log" #有了filename参数就不会直接输出显示到控制台，而是直接写入文件
                    )


class FeatureGet:
    def __init__(self, len_piece):
        self.params = {}
        self.params['len_piece'] = len_piece

    # 特征提取函数
    # 输入一串数据，输出这串数据的一串特征值
    def featureget_line(self, df_line):
        time_std = df_line.std()  # 标准差
        time_max = df_line.max()  # 最大值
        time_min = df_line.min()  # 最小值
        time_skew = df_line.skew()  # 偏度
        time_kurt = df_line.kurt()  # 峭度
        time_rms = np.sqrt(np.square(df_line).mean())  # 均方根
        time_amp = np.abs(df_line).mean()
        time_smr = np.square(np.sqrt(np.abs(df_line)).mean())
        time_boxing = time_rms / (abs(df_line).mean())  # 波形因子
        time_fengzhi = (max(df_line)) / time_rms  # 峰值因子
        time_maichong = (max(df_line)) / (abs(df_line).mean())  # 脉冲因子

        # ----------  freq-domain feature,15
        # 采样频率25600Hz
        df_fftline = fftpack.fft(df_line.tolist())
        freq_fftline = fftpack.fftfreq(len(df_line), 1 / 25600)
        df_fftline = abs(df_fftline[freq_fftline >= 0])
        freq_fftline = freq_fftline[freq_fftline >= 0]
        # 基本特征,依次为均值，标准差，最大值，最小值，均方根，中位数，四分位差，百分位差
        freq_mean = df_fftline.mean()
        freq_iqr = np.percentile(df_fftline, 75) - np.percentile(df_fftline, 25)
        # f2反映频谱集中程度
        freq_f2 = np.square((df_fftline - freq_mean)).sum() / (len(df_fftline) - 1)
        # f5 f7 f8反映主频带位置
        freq_f5 = np.multiply(freq_fftline, df_fftline).sum() / df_fftline.sum()
        freq_f7 = np.sqrt(np.multiply(pow(freq_fftline, 4), df_fftline).sum()) / np.multiply(np.square(freq_fftline),
                                                                                             df_fftline).sum()
        freq_f8 = np.multiply(np.square(freq_fftline), df_fftline).sum() / np.sqrt(
            np.multiply(pow(freq_fftline, 4), df_fftline).sum() * df_fftline.sum())
        # ----------  timefreq-domain feature,12
        # 5级小波变换，最后输出6个能量特征和其归一化能量特征
        cA3, cD3, cD2, cD1 = pywt.wavedec(df_line, 'db10', level=3)
        ener_cD3 = np.square(cD3).sum()
        ener_cD2 = np.square(cD2).sum()
        ener_cD1 = np.square(cD1).sum()
        ener = ener_cD1 + ener_cD2 + ener_cD3
        ratio_cD3 = ener_cD3 / ener

        return_list_all = [time_std, time_max, time_min, time_skew, time_kurt, time_rms, time_amp, time_smr,
                           time_boxing,
                           time_fengzhi, time_maichong,
                           freq_mean, freq_iqr, freq_f2, freq_f5, freq_f7, freq_f8, ener_cD3, ener_cD2, ener_cD1,
                           ratio_cD3]
        return return_list_all

    #特征提取主函数，输入为：全部数据表字典{表名:数据dataframe}，时间窗口
    def featureget(self, df_dict):
        return_dict = {}
        for name in df_dict:
            print('开始特征提取:', name)
            # 读取文件
            file = df_dict[name]
            feature_normal = []
            # 根据文件中的列名创建属性行
            # 依次为
            # 时域：标准差，最大值，最小值，均方根，整流平均值，方根均值
            # 频域：均值，四分位差，一级二级小波变换等
            all_columns = ['time_std', 'time_max', 'time_min', 'time_skew', 'time_kurt', 'time_rms', 'time_amp',
                              'time_smr', 'time_boxing', 'time_fengzhi', 'time_maichong', 'freq_mean',
                              'freq_iqr', 'freq_f2', 'freq_f5', 'freq_f7', 'freq_f8', 'ener_cD3',
                              'ener_cD2', 'ener_cD1', 'ratio_cD3']
            full_columns = []
            for column in file:
                full_columns.extend([column + '_' + j for j in all_columns])
            # 特征提取
            for i in range(0, file.shape[0], self.params['len_piece']):  # 使用时间窗,多余数据丢弃
                feature_line = []
                for j in range(0, file.shape[1]):  # 扫描列
                    feature_line.extend(self.featureget_line(file.iloc[i:i + self.params['len_piece'], j]))  # 输入一列数据，输出一行参数
                feature_normal.append(feature_line)
            return_dict[name] = pd.DataFrame(feature_normal,columns=full_columns)
            print('特征提取完成:', name)
            print(return_dict[name])
        return return_dict

class LocalApi:
    #输入参数为：上传url，下载url，自定义查询语句
    def __init__(self, url_delete, url_load, url_save, db_load, db_save, len_piece):
        self.url_delete = url_delete
        self.url_load = url_load #下载url
        self.url_save = url_save #上传url
        self.collist = []        #已处理的表名
        self.db_load = db_load
        self.db_save = db_save

        self.len_piece = len_piece #窗口大小

    #删除数据
    def delete_data(self):
        request_dict = {}
        request_dict['database'] = self.db_save
        request_dict = json.dumps(request_dict, ensure_ascii=False)
        headers = {'Content-Type': 'application/json'}
        result = requests.get(self.url_delete, headers=headers, data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
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
        result = requests.get(self.url_load, headers=headers,
                              data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
        clist = result.json()['data']  # 获得list类型的表名列表

        new_col = []
        for col in clist:
            if col not in self.collist:
                self.collist.append(col)
                new_col.append(col)
        return new_col

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
            result = requests.get(self.url_load, headers=headers, data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
            clist = str(result.json()['data'])  # 获得数据表
            if clist:
                #规范json格式
                clist = clist.replace("'", '"').replace("true", "True").replace("false", "False").replace("None", "null")
                print(clist)
                json_data_dict = json.loads(clist)  #输此处json_data_dict为一个字典
                json_data_dict = json_data_dict['data']
                #将json文件转化为Dataframe格式
                return_df = pd.DataFrame(json_data_dict['data'], columns=json_data_dict['columns'], index=json_data_dict['index'])
                return_dict[table]=return_df
        return return_dict

    def upload_data(self, return_df_dict):
        for file in return_df_dict:
            print('======================')
            print('upload start:', file)
            request_dict = {}
            request_dict['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            request_dict['data'] = return_df_dict[file].to_json(orient="split", force_ascii=False)
            if request_dict['data']:
                request_dict['database'] = self.db_save
                request_dict['save_option'] = 'mongodb'
                request_dict['save_name'] = file
                request_dict['data_type'] = 'Dataframe'
                # request_dict['transmit_to'] = 'directory'
                headers = {'Content-Type': 'application/json'}
                try:
                    result = requests.post(self.url_save, headers=headers, data=json.dumps(request_dict, ensure_ascii=False))  # 发送查询
                    print('result=', result)
                except Exception as e:
                    print('transmit error:', e)
                    logging.error('transmit error:', e)
                print('upload finished:', file)

    def run(self):
        self.delete_data()
        while 1:
            print('checking')
            new_col=self.data_detect()
            if new_col:
                df_dict = self.download_data(new_col)
                f_get = FeatureGet(self.len_piece)
                return_df_dict = f_get.featureget(df_dict)
                self.upload_data(return_df_dict)
            time.sleep(5)

def main():
    #定义服务器ip地址和端口号
    ip = 'xxx.xxx.xxx.xxx'
    port = '5000'

    #定义窗的大小
    len_piece = 2600

    url_delete = 'http://%s:%s/keshe_middle_platform/api/v1/delete'%(ip, port)
    url_load = 'http://%s:%s/keshe_middle_platform/api/v1/load'%(ip, port)
    url_save = 'http://%s:%s/keshe_middle_platform/api/v1/save'%(ip, port)
    db_load = 'keshe_dataset'
    db_save = 'keshe_featureset'
    app = LocalApi(url_delete, url_load, url_save, db_load, db_save, len_piece)
    app.run()


if __name__ == '__main__':
    main()
