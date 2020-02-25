# -*- coding: utf-8 -*-
import json
import base64
from collections import namedtuple
from bs4 import BeautifulSoup as BS
from requests import get, post, Session

"""
spider 提供了完整功能的实现 Spider类
"""
# 子进程信息, 第几个预约请求, 是否成功
ProcessState = namedtuple("ProcessState", ["index", "state"])


class CaptchaHandler:
    """ CaptchaHandler 用于识别图形验证码
    """
    @classmethod
    def parse_image(cls, image) -> str:
        """识别验证码
        :param image: 图形验证码图片
        :return: str, 验证码的文字
        """
        api_post_url = "http://www.bingtop.com/ocr/upload/"
        # with open(img_url, 'rb') as pic_file:
        #     img64 = base64.b64encode(pic_file.read())
        params = {
            "username": "liulu",
            "password": "19981229",
            "captchaData": base64.b64encode(image),
            "captchaType": 1000
        }
        response = post(api_post_url, data=params)

        # 连接打码平台失败
        if not response.status_code == 200:
            return ""
        data = json.loads(response.text)
        # 出错则 message 非空
        if data["message"]:
            return ""
        return data["recognition"]


class Spider:
    """ Spider 实现了完整的预约过程
    """
    # 青岛政务 url
    base_url = "http://"
    post_url = "http://"
    headers = {

    }

    def __init__(self, order: dict):
        """ Spider 构造方法
        :param order, 一次的预约信息
        """
        # 所有预约信息
        self.order = order
        self.session = Session()

    def subscribe(self, index: int, queue):
        """ 为一条预约信息预约
        :param index, 为该进程分配的
        :param queue, 保存进程信息的队列
        :return: 是否预约成功
        """
        r = self.session.get(self.base_url, headers=self.headers)
        if not r.status_code == 200:
            # return False
            queue.push(ProcessState._make([index, False]))
            return

        # TODO 解析验证码图片
        image = ""

        captcha = CaptchaHandler.parse_image(image)
        self.order["captcha"] = captcha

        # 提交表单
        r = self.session.post(self.post_url, headers=self.headers, data=self.order)
        if not r.status_code == 200:
            queue.push(ProcessState._make([index, False]))
            return

        # TODO 解析返回的 json
        r = json.loads(r.text)
        if r["status"] == "成功":
            queue.push(ProcessState._make([index, True]))
        else:
            queue.push(ProcessState._make([index, False]))
