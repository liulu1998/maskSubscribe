# -*- coding: utf-8 -*-
import json
import base64
from collections import namedtuple
from requests import get, post, Session
from requests.exceptions import Timeout, ConnectionError

"""
spider 提供了完整功能的实现 Spider类
"""
# 子进程信息, 第几个预约请求, 是否成功, 返回信息
PState = namedtuple("PState", ["id", "state", "msg"])


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

        params = {
            "username": "",
            "password": "",
            "captchaData": base64.b64encode(image),
            "captchaType": 1000
        }

        if not params["username"] or not params["password"]:
            raise ValueError("打码平台用户信息不完整")

        response = post(api_post_url, data=params)

        # 连接打码平台失败
        if not response.status_code == 200:
            return ""
        data = json.loads(response.text)

        # 出错则 message 非空
        if data["code"] != 0:
            return ""
        return data["data"]["recognition"]


class SingleSpider:
    """ Spider 实现了完整的预约过程
    """
    # 青岛政务 url
    base_url = "http://kzyynew.qingdao.gov.cn:81/dist/index.html"
    get_url = "http://kzyynew.qingdao.gov.cn:81/kz/getAreaList"
    sfPage_url = "http://kzyynew.qingdao.gov.cn:81/kz/sfPage"
    captcha_url = "http://kzyynew.qingdao.gov.cn:81/kz/captcha"
    post_url = "http://kzyynew.qingdao.gov.cn:81/kz/addSforder"

    success_msg = "正在预约请等待短信通知"

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi K20 Pro Build/QKQ1.190825.002; wv) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2" +
                      "TBS/45016 Mobile Safari/537.36 MMWEBID/3704 MicroMessenger/7.0.10.1580(0x27000AFE) Process/tools" +
                      " NetType/WIFI Language/zh_CN ABI/arm64",
        "Host": "kzyynew.qingdao.gov.cn:81"
    }

    def __init__(self, order: dict, index: int):
        """ Spider 构造方法
        :param order, 一次的预约信息
        """
        # 一条预约信息
        self.order = order
        self.index = index
        self.session = Session()
        # 多进程中无法修改对象的标志位属性 (?), 故未在对象内部加入是否成功的标志位属性
        # 而是把结果信息 写入外部的数据结构

    def subscribe(self) -> PState:
        """ 为一条预约信息预约
        """
        pre_url_list = [self.base_url, self.get_url, self.captcha_url]
        for url in pre_url_list:
            try:
                r = self.session.get(url, headers=self.headers)
            except ConnectionError or Timeout:
                return PState._make([self.index, False, "网络问题"])
            except r.status_code != 200:
                return PState._make([self.index, False, f"青岛政务:{r.status_code}"])

        # 下载验证码
        image = r.content
        # 识别验证码
        captcha = CaptchaHandler.parse_image(image)
        if not captcha:
            return PState._make([self.index, False, "验证码识别错误"])
        # 表单添加 验证码参数
        self.order["capval"] = captcha
        # 提交表单
        r = self.session.post(self.post_url + f"?capval={captcha}",
                              headers=self.headers, 
                              json=self.order)
        r = json.loads(r.text)

        if self.success_msg in r["msg"]:
            return PState._make([self.index, True, r["msg"]])

        return PState._make([self.index, False, r["msg"]])
