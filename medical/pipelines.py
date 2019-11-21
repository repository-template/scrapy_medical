# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# class MedicalPipeline(object):

#     def process_item(self, item, spider):
#         print('-------MedicalPipeline', item)
#         return item

from pymongo import MongoClient


class MongodbPipeline(object):

    def __init__(self, host, port, db, table):
        self.host = host
        self.port = port
        self.db = db
        self.table = table

    @classmethod
    def from_crawler(cls, crawler):
        """
        Scrapy会先通过getattr判断我们是否自定义了from_crawler，有则调它来完成实例化
        """
        HOST = crawler.settings.get('HOST')
        PORT = crawler.settings.get('PORT')
        DB = crawler.settings.get('DB')
        TABLE = crawler.settings.get('TABLE')

        return cls(HOST, PORT, DB, TABLE)

    def open_spider(self, spider):
        """
        爬虫刚启动时执行一次
        """
        # self.client = MongoClient('mongodb://%s:%s@%s:%s' %(self.user,self.pwd,self.host,self.port))
        self.db_client = MongoClient(host=self.host, port=self.port)

    def close_spider(self, spider):
        """
        爬虫关闭时执行一次
        """
        self.db_client.close()

    # 每个item pipeline组件都需要调用该方法，这个方法必须返回一个 Item (或任何继承类)对象。
    def process_item(self, item, spider):
        # 操作并进行持久化
        d = dict(item)
        if all(d.values()):
            self.db_client[self.db][self.table].insert(d)
            print("添加成功一条")

        return item
