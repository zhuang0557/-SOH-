"""
    @Time    : 2023/1/13 11:30
    @Author  : mz
    @FileName: features_extraction.py
    @Brief:  衍生特征提取方法
"""

import inspect
import math
import scipy
import numpy as np
from scipy import stats
from scipy.interpolate import interp1d
from scipy.misc import derivative


class FeatureExtraction():
    """
    衍生特征提取主类
        NOTES:
            --用恒流的数据，但是不采用完整恒流过程来生成特征，取截止点之前的某段时间，忽略起始点附近数值
            --恒流的截止点 (break point)（也即：恒压的起始点）
            --时间，电流，电压，容量字段特征长度一致

            假定恒流的截止点为t。
            1）	用t往前10分钟、20分钟、… X分钟内的恒流充电电压曲线为基础，生成CC-V相关特征。
            2）	用t往后5分钟、10分钟、… Y分钟内的恒压充电电流曲线为基础，生成CV-I相关特征。

            设定特定电压点V。
            1）	以V为起始点，选择ΔV为0.2V、0.5V、0.8V、…等电压间隔的恒流充电曲线为基础，生成充电容量变化量生成特征，即CC-Q相关特征。
            2）	设置不同的V和ΔV，以保证大部分数据都可以生成所需特征。

            相关特征: 曲线的几何特性，数据的统计特性

                CC-V	self.voltage_interval
                        10min/20min/25min
                                                截止点斜率
                                                电压曲线最大斜率
                                                平均值
                                                偏度
                                                峰度
                                                统计标准差
                                                最大压差
                                                充电电压曲线围成的面积
                CC-I	self.current_interval
                        5min/10min/15min
                                                截止点斜率
                                                电压曲线最大斜率
                                                平均值
                                                偏度
                                                峰度
                                                统计标准差
                                                最大压差
                                                充电电压曲线围成的面积
                CC-Q	self.anchor_voltage
                        V = 3250mv
                        self.delta_voltage
                        Δv = 0.2v/0.5v/0.8v
                保证大部分数据都可以生成所需要的特征	最大容量
                                                容量均值
                                                容量方差
    """

    def __init__(self,charge_name,time,current,voltage,capacity):
        assert len(time) == len(current) == len(voltage) == len(capacity)
        self.charge_name = charge_name
        self.time = time
        self.current = current
        self.voltage = voltage
        self.capacity = capacity
        # self.voltage_interval = 20               #[0-150]
        self.current_interval = 100                #[0-150]
        self.anchor_voltage = 3250                 #2500,2750,3025,3250...
        self.delta_voltage = 300                   #[200,500,800] mv
        self.knee_index = self.get_knee_point()

    def Ah_integral(self):
        """
        安时积分计算电池容量数值
        :return: capacity
        """
        capacity = [0]
        q = 0
        for i in range(len(self.time) - 1):
            q += (self.time[i + 1] - self.time[i]) * self.current[i + 1]
            capacity.append(math.ceil(q / 60))
        return capacity

    def get_knee_point(self):
        """
        获取电压截止点 3.4、3.45、3.5、3.50、3.6
        :return:break point index
        """
        knee_index = 1
        for i in range(len(self.voltage) - 1):
            if self.voltage[i] >= 3400:  # 取截止电压点
                knee_index = i
                break
        if knee_index == 0 :
            # print("电池类型名称：",self.charge_name)
            pass
        return knee_index

    def get_interval(self,interval):
        """
        根据指定的区间长度查找起始点和截至点的索引
        :param interval: 区间长度
        :return: 返回满足区间长度的起始点 、截至点索引
        """
        t_start = self.get_knee_point() - interval
        if t_start <= 0 :
            t_start = 0
        t_end = self.get_knee_point()
        return t_start, t_end

    """
        ===================================
            CC-V
            电压截止点前1min， 电压曲线相关特征提取
        ===================================
    """
    def slope_keen_point_charging_voltage_curve(self):
        """
        从充电开始到第一次上截止电压时，截止电压时曲线的斜率
        :return: 充电电压曲线拐点斜率
        """
        try:
            f1 = interp1d(self.time, self.voltage)
            slope_keen_point = derivative(f1, self.time[self.knee_index], dx=1e-8)
            return slope_keen_point
        except:
            return 'nan'

    def maximum_slope_charging_voltage_curve(self):
        """
        恒流截止前25min，电压曲线最大斜率
        :return: 返回电压曲线的最大斜率
        """
        try :
            start,keen = self.get_interval(self.current_interval)

            f1 = interp1d(self.time, self.voltage)

            max_slope = []
            for v in [v + 1e-08 if v == 0 else v for v in self.time[start:keen]]:
                max_slope.append(derivative(f1, v, dx=1e-8))
            return max(max_slope)
        except:
            return 'nan'


    def average_voltage_constant_current_charging(self):
        """
        恒流截止前25min，电压平均值
        :return: 平均值
        """
        start, keen = self.get_interval(self.current_interval)
        voltage_average = np.average(self.voltage[start:keen])
        return voltage_average

    # def skew_voltage_constant_current_charging(self):
    #     """
    #     恒流截止前25min，电压偏度
    #     :return: 偏度
    #     """
    #     start, keen = self.get_interval(self.current_interval)
    #     voltage_skew = stats.skew(self.voltage[start:keen]) # 偏度
    #
    #     return voltage_skew
    #
    #
    # def surtosis_voltage_constant_current_charging(self):
    #     """
    #      恒流截止前25min，电压峰度
    #     :return: 峰度
    #     """
    #     start, keen = self.get_interval(self.current_interval)
    #     voltage_surtosis = stats.kurtosis(self.voltage[start:keen])  # 峰度
    #
    #     return voltage_surtosis

    def stad_voltage_constant_current_charging(self):
        """
        恒流截止前25min，电压标准差
        :return: 标准差
        """
        start, keen = self.get_interval(self.current_interval)

        voltage_stad = np.std(self.voltage[start:keen])  # 标准差
        return voltage_stad

    def maximum_differential_constant_current_charging(self):
        """
        恒流截止前25min，最大压差
        :return: 最大压差
        """
        start, keen = self.get_interval(self.current_interval)

        maximun_differential = self.voltage[keen] - self.voltage[start]
        return maximun_differential



    def curve_area_constant_current_charging_voltage(self):
        """
        恒流截止前25min，充电电压曲线围成的面积
        :return:积分面积
        """
        integrals = []  # 用于存储积分
        start, keen = self.get_interval(self.current_interval)
        for i in range(start, keen):  # 计算梯形的面积，由于是累加，所以是切片"i+1"
            integrals.append(scipy.integrate.trapz(self.voltage[:i + 1], self.time[:i + 1]))
        if integrals:
            return integrals[-1]
        else:
            return 'nan'

    def maximum_capacity_constant_current_charging(self):
        """
        电压截止点时容量
        :return:恒流阶段截止点容量
        """
        capacity = self.Ah_integral()
        break_point_index = self.get_knee_point()
        return capacity[break_point_index]


    """
    ===================================
        CC-Q
        恒压起始前10min， 电容相关特征提取
    ===============================+====
    """
    def get_delta_voltage_index(self):
        """
        取给定的锚点电压最近的数值索引 ,以及delta V 后的电压索引位置
        :return: start: anhor v nearest index ;
                 end :  anhor v plus delta v index
        """
        array = np.asarray(self.voltage)
        start = (np.abs(array - self.anchor_voltage)).argmin()

        end = (np.abs(array - (self.anchor_voltage + self.delta_voltage))).argmin()
        if start == end:
            end += 1
        return start, end

    def get_max_capacity(self):
        """
        指定电压区间的最大容量
        :return: max_capacity
        """
        start, end = self.get_delta_voltage_index()
        if self.capacity[start:end]:
            max_capacity = max(self.capacity[start:end])

            return max_capacity
        else:
            return 'nan'

    def get_average_capacity(self):
        """
        指定电压区间的容量平均值
        :return: average_capacity
        """
        start, end = self.get_delta_voltage_index()
        average_capacity = np.average(self.capacity[start:end])
        return average_capacity

    def get_var_capacity(self):
        """
        指定电压区间容量的方差
        :return: var_capacity
        """
        start, end = self.get_delta_voltage_index()
        var_capacity = np.var(self.capacity[start:end])
        return var_capacity




    def run(self):
        result = []

        result1 = self.slope_keen_point_charging_voltage_curve()                      # 截止点时电压斜率
        result2 = self.maximum_slope_charging_voltage_curve()
        result3 = self.average_voltage_constant_current_charging()
        # result4 = self.skew_voltage_constant_current_charging()
        # result5 = self.surtosis_voltage_constant_current_charging()
        result6 = self.stad_voltage_constant_current_charging()
        result7 = self.maximum_differential_constant_current_charging()
        result8 = self.curve_area_constant_current_charging_voltage()
        result9 = self.maximum_capacity_constant_current_charging()
        result10 = self.get_max_capacity()
        result11 = self.get_average_capacity()
        result12 = self.get_var_capacity()

        result.extend([result1, result2, result3,result6,result7,result8,result9,result10,result11,result12])



        return result





















