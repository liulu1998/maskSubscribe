# -*- coding: utf-8 -*-
import json
import pickle
from json import JSONDecodeError

"""
info 包 提供了 InfoHandler 类, 用于解析磁盘上的配置文件
"""


class InfoHandler:
    """ InfoHandler 用来解析配置文件
    """
    @classmethod
    def parse_info(cls, info_path: str, pkl_path: str) -> (str, list):
        """ 解析配置文件, 返回个人预约信息
        :param info_path: str, 个人预约信息路径
        :param pkl_path: str, 序列化的地址映射文件路径
        :return: dict, 预约信息
        """
        try:
            with open(pkl_path, "rb") as f:
                address_info = pickle.load(f)

            with open(info_path, "r") as f:
                orders = json.load(f)
            # orders =
            start_time = "09:30"
            # TODO 解析成最终的信息
            return start_time, orders
        except FileNotFoundError or ValueError or JSONDecodeError:
            return None, []
