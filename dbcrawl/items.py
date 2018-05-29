# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DbcrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    UserName = scrapy.Field()
    DoubanId = scrapy.Field()
    Location = scrapy.Field()
    ReaderTags = scrapy.Field()
    Comment = scrapy.Field()
    FavoriteAuthors = scrapy.Field()