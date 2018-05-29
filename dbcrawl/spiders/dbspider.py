# -*- coding: utf-8 -*-
import scrapy
from dbcrawl.items import DbcrawlItem


class DbspiderSpider(scrapy.Spider):
    name = 'dbspider'
    allowed_domains = ['book.douban.com', 'www.douban.com']
    start_urls = [
        'https://book.douban.com/subject/25862578/comments/hot?p=321']
    commentsUrltpl = 'https://book.douban.com/subject/25862578/comments/hot?p={page}'

    def parse(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        pagesCount = 321
        try:
            pagesCount = response.meta["pagesCount"]
        except KeyError as e:
            pagesCount = 321
            pass
        readerDivs = response.css(
            '#comments > ul li.comment-item')
        readersNum = len(readerDivs)
        if readersNum > 0:
            pagesCount = pagesCount + 1
            print("====================================")
            print("====================================\n\n")
            print("访问评论第{}页".format(pagesCount))
            print("====================================")
            for x in readerDivs:
                readerItem = DbcrawlItem()
                p = x.css(
                    'div.comment > h3 > span.comment-info > a::attr(href)').extract()[0].strip()
                comment = x.css('div.comment > p::text').extract()[0].strip()
                readerItem['Comment'] = comment
                yield scrapy.Request(p, meta={"readerItem": readerItem}, callback=self.parseReaderInfo)

            yield scrapy.Request(self.commentsUrltpl.format(page=pagesCount), callback=self.parse, meta={"pagesCount": pagesCount})

    def parseReaderInfo(self, response):
        try:
            readerItem = response.meta['readerItem']
            userName = response.css(
                '#db-usr-profile > div.info > h1::text').extract()[0][0:-3].strip()
            location = response.css(
                '#profile > div > div.bd > div.basic-info > div > a::text').extract()[0].strip()
            DoubanId = response.url.split("/")[-2]
            print("豆瓣 id from response url:", response.url)
            readerItem['UserName'] = userName
            readerItem['Location'] = location
            readerItem['DoubanId'] = DoubanId

            readTagsUrl = self.constructReaderTagsUrl(response.url)
            # 访问读者的读书标签
            yield scrapy.Request(readTagsUrl, meta={"readerItem": readerItem}, callback=self.parseReaderTags)
        except IndexError:
            pass

    def parseReaderTags(self, response):
        readerItem = response.meta["readerItem"]
        tagDivs = response.css(
            '#content > div.grid-16-8.clearfix > div.aside > ul li')
        if len(tagDivs) > 0:
            tags = []
            for x in tagDivs:
                tag = x.css('a::text').extract()[0]
                frequency = x.css('span::text').extract()[0]
                tags.append({"tag": tag, "frequency": frequency})
            readerItem['ReaderTags'] = tags

            # 访问读者收藏的作者
            DoubanId = readerItem['DoubanId']
            favAuthorsUrlTpl = 'https://book.douban.com/people/{}/authors'
            favAuthorsUrl = favAuthorsUrlTpl.format(readerItem['DoubanId'])
            print("豆瓣id:", readerItem['DoubanId'])
            yield scrapy.Request(favAuthorsUrl, meta={"readerItem": readerItem}, callback=self.parseFavoriteAuthors)
        else:
            pass

    def parseFavoriteAuthors(self, response):
        print("访问", response.url, "favorite authors")

        readerItem = response.meta['readerItem']
        authorSelectors = response.css(
            "#content > div.grid-16-8.clearfix > div.article > div div.item")
        # if authorSelectors != []:
        #     from scrapy.shell import inspect_response
        #     inspect_response(response, self)

        authors = []
        for x in authorSelectors:
            try:
                author = x.css('div.info > ul > li.title > a > em::text').extract()[
                    0].strip()
                authors.append(author)
            except IndexError:
                pass
        readerItem['FavoriteAuthors'] = authors
        yield readerItem

    def constructReaderTagsUrl(self, peopleHomePageUrl):
        return peopleHomePageUrl.replace("www", "book", 1) + 'collect'
