# -*- coding: utf-8 -*-
import time
import datetime
import multiprocessing

from spider.spider import Spider
from spider.info import InfoHandler

"""
main包 提供 MainScheduler主调度类
"""

# 进程数
NUM_PROCESS = 4


class MainScheduler:
    """ 主调度类, 以多进程的方式并发完成多个预约
    """
    def __init__(self, info_path: str, pkl_path: str):
        """ MainScheduler 构造方法
        :param info_path: 预约信息文件路径
        :param pkl_path: 序列化的地址映射文件路径
        """
        start_time, orders = InfoHandler.parse_info(info_path, pkl_path)
        if not start_time or not orders:
            raise ValueError("配置文件解析失败")
