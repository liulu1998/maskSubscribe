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
# 最大尝试次数
MAX_RETRY = 30


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

        self.start_time = start_time
        self.orders = orders

    def run(self):
        """ 多进程预约
        """
        # 为每条预约信息构造爬虫
        spiders = [Spider(order) for order in self.orders]
        # 是否完成
        # achieved = [False] * len(spiders)
        # 进程安全的队列
        # queue = multiprocessing.Manager().Queue(len(spiders))
        # 进程池
        pool = multiprocessing.Pool(NUM_PROCESS)

        # TODO 等待 start_time
        # while True:
        #     time.sleep(2)

        flag = False
        # 尝试 MAX_RETRY 轮
        for epoch in range(MAX_RETRY):
            print(f"---- 第{epoch+1}次尝试 ----")
            # 未完成的任务加入进程池
            # for i, (spider, state) in enumerate(zip(spiders, achieved)):
            #     if not state:
            #         pool.apply_async(func=spider.subscribe, args=(i, queue))
            for spider in spiders:
                if not spider.achieved:
                    pool.apply_async(func=spider.subscribe)
            # 开始多进程运行
            pool.close()
            pool.join()

            states = [spider.achieved for spider in spiders]
            if list(set(states))[0]:
                break
            # 处理完成情况
            # while not queue.empty():
            #     p_state = queue.get()
            #     achieved[p_state.index] = p_state.state

            # if list(set(achieved))[0]:
            #     flag = True
            #     break
            # 避免爬取过快
            time.sleep(0.2)

        if flag:
            print("---- 成功 嘻嘻嘻 ----")
        else:
            print("---- 失败 55555 ----")


if __name__ == '__main__':
    scheduler = MainScheduler(info_path="./info.json", pkl_path="./map.pkl")
    scheduler.run()
