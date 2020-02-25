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
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi K20 Pro Build/QKQ1.190825.002; wv) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2" +
                      "TBS/45016 Mobile Safari/537.36 MMWEBID/3704 MicroMessenger/7.0.10.1580(0x27000AFE) Process/tools" +
                      " NetType/WIFI Language/zh_CN ABI/arm64",
        "Host": "kzyynew.qingdao.gov.cn:81"
    }

    def __init__(self, order: dict):
        """ Spider 构造方法
        :param order, 一次的预约信息
        """
        # 所有预约信息
        self.order = order
        self.session = Session()
        self.achieved = False

    def subscribe(self):
        """ 为一条预约信息预约
        :param index, 为该进程分配的
        :param queue, 保存进程信息的队列
        :return: 是否预约成功
        """
        r = self.session.get(self.base_url, headers=self.headers)
        if not r.status_code == 200:
            # return False
            # queue.put(ProcessState._make([index, False]))
            return

        # TODO 解析验证码图片
        image = ""

        captcha = CaptchaHandler.parse_image(image)
        self.order["captcha"] = captcha

        # 提交表单
        r = self.session.post(self.post_url, headers=self.headers, data=self.order)

        if not r.status_code == 200:
            # queue.put(ProcessState._make([index, False]))
            return

        # TODO 解析返回的 json
        r = json.loads(r.text)
        if r["status"] == "成功":
            # queue.put(ProcessState._make([index, True]))
            self.achieved = True
        # else:
        #     queue.put(ProcessState._make([index, False]))
