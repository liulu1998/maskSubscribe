# -*- coding: utf-8 -*-
import time
import datetime
import threading
import multiprocessing
from functools import reduce

from spider.web import SingleSpider
from spider.info import InfoHandler

"""
main包 提供 MainScheduler主调度类
"""

# 进程数
NUM_PROCESS = 4
# 最大尝试次数
MAX_RETRY = 2


class MultiSpider:
    """ 主调度类, 以多进程的方式并发完成多个预约
    """
    def __init__(self, info_path: str):
        """ MainScheduler 构造方法

        :param info_path: 预约信息文件路径
        """
        stime, orders = InfoHandler.parse_info(info_path)
        if not stime or not orders:
            raise ValueError("配置文件解析失败")

        self.start_time = stime
        self.orders = orders

    def run(self):
        """ 多进程预约
        """
        # 为每条预约信息构造爬虫
        spiders = [SingleSpider(order) for order in self.orders]

        flag = False
        # 尝试 MAX_RETRY 轮
        for epoch in range(MAX_RETRY):

            pool = multiprocessing.Pool(NUM_PROCESS)
            for spider in spiders:
                if not spider.achieved:
                    pool.apply_async(func=spider.subscribe)
            # 开始多进程运行
            pool.close()
            pool.join()
            # 所有爬虫的完成情况, 依次做逻辑与
            states = map(lambda x: x.achieved, spiders)
            if reduce(lambda x, y: x and y, states):
                flag = True
                break

            # 避免爬取过快
            time.sleep(0.1)

        if flag:
            print("---- 成功 嘻嘻 ----")
        else:
            print(f"---- 尝试了{MAX_RETRY}次 ----\n---- 失败 5555 ----")


if __name__ == '__main__':
    s = MultiSpider(info_path="./info.json")

    print(f"---- 解析信息成功 ----")

    t = datetime.date.today()
    start_time = datetime.datetime.strptime(f"{t.year}-{t.month}-{t.day} {s.start_time}:0",
                                            "%Y-%m-%d %H:%M:%S")
    cur_time = datetime.datetime.now()

    interval = (start_time - cur_time).total_seconds()
    if interval >= 0:
        timer = threading.Timer(interval, s.run)
        print(f"---- 任务将在 {s.start_time} 开始 ----")
        timer.start()
    else:
        print("---- 明天将持续多久?\n---- 比永恒多一天")
