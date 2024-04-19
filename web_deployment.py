#coding:utf-8

from flask import Flask
import pickle as pk
import json
import math
from gevent import pywsgi
from sql_connection import sql_conn as conn
from feature_extraction.features_extraction_2 import FeatureExtraction
from flask import Flask,request
import requests
from util.configure import training_args
args = training_args()
import warnings
warnings.filterwarnings('ignore')

loaded_model = pk.load(open(r"D:\bms\model\15ah_model_1221.pickle.dat", "rb"))

app = Flask(__name__)
results  = {
    "msg": "success",
    "status": 1,
    "data": None
}

@app.route("/",methods = ["POST"])
def capacity_estimation():
    content = []
    resss = request.get_data()

    for i in json.loads(resss):
        print(i)
        sub_data = conn.get_connection(i)

        cpu_cores = multiprocessing.cpu_count()  # 获取CPU核心数量
        with ThreadPool(cpu_cores + 1) as pool:  # 设置线程池大小为CPU核心数量加1
            results = pool.map(process_file, listPath)

        for v in sub_data.groups:


            if len(v):
                results = {
                    "msg": "success",
                    "status": 1,
                    "data": None
                }
                one_charge = {}
                charge = sub_data.get_group(v)
                # print(charge)

                one_charge["max_id"] = max(charge["id"])
                one_charge["testNum"] = v[0]
                one_charge["deviceId"] = v[1]
                one_charge["channelId"] = v[2]
                one_charge["capacity"] = 0
                content.append(one_charge)

                # time = list(charge['stepTime'])
                # time = time[::60]
                # current = list(charge["electric"] * 1000)
                # # current = current[::60]
                # voltage = list(charge["voltage"] * 1000)
                # # voltage = voltage[::60]
                # capacity = list(charge["capacity"] * 1000)
                # # capacity = capacity[::60]
                # charge_name = None
                # f = FeatureExtraction(charge_name, time, current, voltage, capacity)
                # result = f.run()
                # # print(result)
                # if 'nan' not in result:
                #     if None not in result:
                #         result = [0.0 if math.isnan(x) else x for x in result]
                #         # print(result)
                #         y_pred = loaded_model.predict([result])
                #         one_charge["capacity"] = float(y_pred)
                #         content.append(one_charge)
                #     else:
                #         one_charge["capacity"] = float(0)
                #         content.append(one_charge)
                # else:
                #     one_charge["capacity"] = float(0)
                #     content.append(one_charge)
                results["data"] = content

            else:
                results = {
                    "msg": "fail",
                    "status": 2,
                    "data": None
                }
    for i in content:
        print(i['capacity'])

    json_str = json.dumps(results,indent=6)

    return json_str


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    print("Flsak is providing services ~~")
    server.serve_forever()