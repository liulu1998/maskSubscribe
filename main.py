# -*- coding: utf-8 -*-
import time
import queue
import datetime
import threading
import multiprocessing
from functools import reduce

from spider.info import InfoHandler
from spider.web import SingleSpider, PState

"""
main包 提供 MainScheduler主调度类
"""

# 进程数
NUM_PROCESS = 4
# 最大尝试次数
MAX_RETRY = 3


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
        # 保存爬虫日志, 爬取过程中不 IO
        self.queue = queue.Queue(MAX_RETRY * len(self.orders))

    def run(self):
        """ 多进程预约
        """
        # 为每条预约信息构造爬虫
        spiders = [SingleSpider(order, i) for i, order in enumerate(self.orders)]
        achieved = [False] * len(spiders)
        # 是否无货
        is_empty = False
        flag = False
        total_retry = 0

        # 尝试 MAX_RETRY 轮
        for epoch in range(MAX_RETRY):
            total_retry += 1

            pool = multiprocessing.Pool(NUM_PROCESS)
            results = []

            for state, spider in zip(achieved, spiders):
                if not state:
                    results.append(pool.apply_async(func=spider.subscribe))
            # 开始多进程运行
            pool.close()
            pool.join()

            # 统计完成情况
            for result in results:
                r: PState = result.get()
                achieved[r.id] = r.state
                self.queue.put_nowait(r)
                if "不足" in r.msg or r.msg == "未开始":
                    is_empty = True

            # 全部完成情况做逻辑与
            if reduce(lambda x, y: x and y, achieved):
                flag = True
                break

            if is_empty:
                break

            # 避免爬取过快
            time.sleep(0.1)

        while not self.queue.empty():
            r = self.queue.get()
            print(f"spider[{r.id}] 成功? [{r.state}] 信息: {r.msg}")

        if flag:
            print("---- 成功 嘻嘻 ----")
        else:
            print(f"---- 尝试了{total_retry}次 ----\n---- 失败 5555 ----")


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
