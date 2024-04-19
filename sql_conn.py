"""
    @Time    : 2022/11/11 17:25
    @Author  : clei
    @FileName: sql_conn.py
    @Brief:  链接数据库 查询数据
"""
import pandas as pd
import pymysql
import pandas as pd
import pymysql
from util.configure import training_args
args = training_args()
order_number = args.order_number
""""
columns = [['id', 'type', 'devtype', 'devid', 'subdevid', 'chlid', 'auxid',
       'testid', 'seqid', 'stepid', 'cycleid', 'step_type',
       'volume_partition_no', 'order_number', 'long_time', 'atime', 'voltage',
       'electric', 'capacity', 'power', 'temp', 'create_by', 'create_time',
       'update_by', 'update_time']]
"""



def get_connection(ordernum):


    """
    连接数据库，功能函数
    ordernum : dict
    :return: 每个电池需要的分析数据
    """
    db = pymysql.connect(host='192.168.150.33',
                         port=6606,
                         user='bjx',
                         password='123456',
                         database='test_gk_battery_capacity')
    # db = pymysql.connect(host='192.168.150.62',
    #                      port=3306,
    #                      user='root',
    #                      password='gq1234GQ!%*',
    #                      database='dev_battery_capacity')


    sql = rf"select id,device_id as deviceId,channel_id as channelId,test_num as testNum,step_time as stepTime,voltage,electric,capacity from vp_charge_discharge_record WHERE type = 1 AND test_num = '{ordernum['testNum']}' AND device_id = '{ ordernum ['deviceId']} 'AND channel_id = '{ ordernum ['channelId']}'"

    # sql = rf"select id, ip, devid, subdevid, chlid, order_number, long_time, voltage, electric, capacity  from vp_charge_discharge_record  where type =1 and order_number = '76723525595041792'"
    # print(sql)
    data = pd.read_sql(sql, db)

    data = data[['id',"testNum", "deviceId", 'channelId', 'stepTime', 'voltage', 'electric', 'capacity']]
    print(data)

    sub_data = data.groupby(["deviceId", "testNum",'channelId'])  # 各个电池的分组数据
    #
    return sub_data
#
# if __name__ == '__main__':
#     ordernum = {'testNum':"1691391371569",'deviceId':'2','channelId':"1-7"}
#     sub_data = get_connection(ordernum)
#     for v in sub_data.groups:
#         print(v)

