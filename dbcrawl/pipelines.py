# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient

class DbcrawlPipeline(object):
    def __init__(self):
        self.mongouri = 'mongodb://localhost:27017'

    def open_spider(self, spider):
        self.mongoClient = MongoClient(self.mongouri)
        self.mongoDB = self.mongoClient['douban']
        self.mongoCollection = self.mongoDB['reader']

    def process_item(self, item, spider):
        self.mongoCollection.insert_one(dict(item))
        return item
    
    def close_spider(self, spider):
        self.mongoClient.close()


