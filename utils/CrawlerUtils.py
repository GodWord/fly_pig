# -*- coding:utf-8 -*
import logging

logger = logging.getLogger('crawler.utils')

class CrawlerUtils(object):
    @staticmethod
    def convert_img(driver, img_location):
        import logging
        import os
        from PIL import Image
        tmp_path = './tmp'
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        driver.save_screenshot(os.path.join(tmp_path, 'code.png'))
        try:
            im = Image.open(os.path.join(tmp_path, 'code.png'))

            left = driver.find_element_by_xpath(img_location).location['x']
            top = driver.find_element_by_xpath(img_location).location['y']
            right = driver.find_element_by_xpath(img_location).location['x'] + \
                    driver.find_element_by_xpath(img_location).size['width']
            bottom = driver.find_element_by_xpath(img_location).location['y'] + \
                     driver.find_element_by_xpath(img_location).size['height']

            # 打开本地图片
            im = im.crop((left, top, right, bottom))
            im.save(os.path.join(tmp_path, 'screenshot.png'))
            logger.info('screenshot.png 保存成功')
            os.remove(os.path.join(tmp_path, 'code.png'))
            return True
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def get_user_agent():
        import random
        user_agents = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        ]
        return user_agents[random.randint(0, len(user_agents) - 1)]

    @staticmethod
    def get_headers(str_headers):
        headers = dict(map(lambda x: x.split(':', 1), str_headers.strip().split('\n')))
        headers['User-Agent'] = CrawlerUtils.get_user_agent()
        return headers

    @staticmethod
    def get_generator_by_csv(file_path: str, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding) as file:
            data = file.readlines()
        for values in data:
            keyword_list = values.strip().strip(',').split(',')
            if '' in keyword_list:
                keyword_list.remove('')
            for keyword in keyword_list:
                yield keyword

    @staticmethod
    def get_params_by_url(url):
        from urllib import parse
        params_url = parse.urlsplit(url).query
        params = dict(map(lambda x: x.split('='), params_url.split('&')))
        return params

    @staticmethod
    def get_tag(text, selector):
        from bs4 import BeautifulSoup
        bs = BeautifulSoup(text, 'lxml')
        res = bs.select(selector)
        return res

    @staticmethod
    def get_html(url, headers=None, params=None, is_post=False, **kwargs):
        import requests
        import logging

        if is_post:
            req = requests.post(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        else:
            req = requests.get(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        try:
            req.raise_for_status()
            return req.text
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def get_content(url, headers=None, params=None, is_post=False, **kwargs):
        import requests
        import logging

        if is_post:
            req = requests.post(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        else:
            req = requests.get(url, headers=headers, params=params, **kwargs)
            req.encoding = req.apparent_encoding
        try:
            req.raise_for_status()
            return req.content
        except Exception as e:
            logging.error(e)
            return False

    @staticmethod
    def get_json(url, headers=None, params=None, is_post=False, **kwargs):
        import json
        import logging
        try:
            data = json.loads(CrawlerUtils.get_content(url, headers=headers, params=params, is_post=is_post, **kwargs))
        except Exception as e:
            logging.error(e)
            data = dict()

        return data

    @staticmethod
    def table_exists(table_name, conn):
        import re
        """"判断表是否存在"""
        cur = conn.cursor()
        sql = "show tables;"
        cur.execute(sql)
        tables = [cur.fetchall()]
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]

        if table_name in table_list:
            return True  # 存在返回True
        else:
            return False  # 不存在返回False

    @staticmethod
    def execute_sql(sql, conn):
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        return res

    @staticmethod
    def get_sql_by_dict(table_name, data: dict):
        """
        根据数据字典自动生成sql插入语句
        :param table_name: 表名
        :param data: 字典
        :return: sql, values
        """
        sql = 'insert into {}(%s) values(%s);'.format(table_name)  # 定义数据库插入语句
        columns = tuple(data.keys())  # 取出字典中的key,用作表的列字段
        values = tuple(data.values())  # 取出对应key对应value,用作数据
        sql = sql % ('{}' * len(data), '%s' * len(data))  # 预编译sql语句
        sql = sql.replace(r'}{', '},{').replace(r's%', 's,%')  # 预编译sql语句,各个字段间添加:,
        sql = sql.format(*columns)  # 将columns预编译到sql语句中

        return sql, values

    @staticmethod
    def get_sql_by_list(table_name, columns, values):
        """
        根据数据字典自动生成sql插入语句
        :param table_name: 表名
        :param data: 字典
        :return: sql, values
        """
        if len(columns) != len(values):
            return None, None
        sql = 'insert into {}(%s) values(%s);'.format(table_name)  # 定义数据库插入语句

        sql = sql % ('{}' * len(columns), '%s' * len(columns))  # 预编译sql语句
        sql = sql.replace(r'}{', '},{').replace(r's%', 's,%')  # 预编译sql语句,各个字段间添加:,
        sql = sql.format(*columns)  # 将columns预编译到sql语句中

        return sql, values
