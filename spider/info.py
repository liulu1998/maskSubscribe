# -*- coding: utf-8 -*-
import json
from json import JSONDecodeError

"""
info 包 提供了 InfoHandler 类, 用于解析磁盘上的配置文件
"""


class InfoHandler:
    """ InfoHandler 用来解析配置文件
    """
    @classmethod
    def parse_info(cls, info_path: str) -> (str, list):
        """ 解析配置文件, 返回个人预约信息
        :param info_path: str, 个人预约信息路径
        :return: dict, 预约信息
        """
        try:
            with open(info_path, "r", encoding="utf-8") as f:
                info = json.load(f)

            orders = info["orders"]
            for order in orders:
                order["ordertype"] = 2
                
            return info["startTime"], orders
        except FileNotFoundError or ValueError or JSONDecodeError:
            return None, []
