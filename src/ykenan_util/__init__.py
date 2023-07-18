#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import random
import re
import time
import uuid

from ykenan_log import Logger

from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
# noinspection PyPep8Naming
from selenium.webdriver.support import expected_conditions as EC

from ykenan_util.snowflake import IdWorker

'''
 * @Author       : YKenan
 * @Description  : Util class
'''


class Util:
    """
    初始化文件
    """

    def __init__(self,
                 driver=None,
                 wait=None,
                 is_show=False,
                 is_refresh=False,
                 log_file: str = "YKenan_util",
                 is_form_log_file: bool = True):
        """
        Initialization creation information, public information
        :param driver: 引擎
        :param wait: selenium 等待
        :param is_show: 是否启动无头模式
        :param is_refresh: 是否刷新页面
        :param log_file: Path to form a log file
        :param is_form_log_file: Is a log file formed
        """
        self.log = Logger(name="YKenan_util", log_path=log_file, is_form_file=is_form_log_file)
        self.wait = wait
        self.driver = driver
        self.is_show = is_show
        self.is_refresh = is_refresh

    @staticmethod
    def generate_unique_id() -> str:
        """
        形成数据库中的表
        """
        uuid_: str = str(uuid.uuid1())
        uuid__: str = re.sub("-", "", uuid_)
        id_: int = round(random.Random().random() * 100 % 31)
        unique: str = uuid__ + IdWorker().generator(str(id_))
        # 正常长度不会大于 62, 防止意外, 数据库存储长度为 pow(2,6)
        return unique[1:62]

    def init_driver(self):
        """
        浏览器引擎初始化
        :return: 浏览器引擎
        """
        options = FirefoxOptions()
        # 设置不加载
        options.page_load_strategy = 'normal'
        # 是否设置为无头模式
        if self.is_show:
            # 设置火狐为 headless 无界面模式
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
        # 实例化浏览器对象
        return Firefox(options=options)

    def refresh_handle(self):
        """
        窗口处理, 对 selenium 跳转 URL 的处理
        :return: None
        """
        time.sleep(1)
        # 得到跳转之前的页面
        original_window = self.driver.current_window_handle
        # 获取所有的窗口
        handles = self.driver.window_handles
        # 切换窗口
        for handle in handles:
            if handle != original_window:
                # 关闭前面的窗口
                self.driver.close()
                self.driver.switch_to.window(handle)
        # 刷新和沉睡是为了防止得到的页面代码不全
        time.sleep(1)
        if self.is_refresh:
            self.driver.refresh()

    def is_element_exist(self, xpath):
        """
        判断某个标签是否存在
        :param xpath: xpath 解析的路径
        :return: 是否存在 true: 存在
        """
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except Exception as e:
            self.log.debug(f"标签不存在: {e.args}")
            return False

    def circle_run(self, title_, callback, refresh, i=0):
        """
        回调函数 主要用户 selenium 访问进行获取相关信息为获取到进行重新获取
        :param title_: 是 callback 函数的参数信息
        :param callback: 回调的第一个函数, 主要的执行函数
        :param refresh: 回调的第二个函数, 当第一个 callback 函数出现错误时候进行一定的刷新循环
        :param i: 循环的次数, 也就是 callback 函数执行错误的次数
        :return: 相关信息
        """
        try:
            return callback(title_)
        except Exception as e:
            i += 1
            self.log.warn(f"获取元素失败, 重新获取: {e}")
            print(i)
            if i % 5 == 0:
                refresh()
            elif i % 10 == 0:
                refresh(True)
            return self.circle_run(title_, callback, refresh, i)
