# -*- coding: utf-8 -*-
"""

@author: Viet Lai
"""

import argparse
import scrapy
import io
import json
import logging
import os

from article import Article
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.crawler import CrawlerProcess


class NewsSpider(scrapy.Spider):
    """Summary

    Attributes:
        crawled_history (str): Description
        crawled_pages (list): Description
        link_directory (str): Description
        name (str): Description
    """

    name = "news"
    link_directory = "vietnamnet"
    crawled_history = "history/vietnamnet-history.txt"
    crawled_pages = []
    crawled_ids=[]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """Summary

        Args:
            crawler (TYPE): Description
            *args: Description
            **kwargs: Description

        Returns:
            TYPE: Description
        """
        spider = super(NewsSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        spider.start = kwargs['start']
        spider.end = kwargs['end']
        return spider

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        self.load_crawled_pages()
        url_pattern = 'https://vietnamnet.vn/vn/-{}.html'

        # crawl data for each link
        for id in range(self.start, self.end):
            if id not in self.crawled_ids:
                link = url_pattern.format(id)
                yield scrapy.Request(url=link, callback=self.parse)
            else:
                print('Ignore: ', id)

    def parse(self, response):
        """Summary

        Args:
            response (TYPE): Description
        """
        container = response.css("div.ArticleDetail")[0]
        title = container.css("h1.title").extract_first().strip()
        title = BeautifulSoup(title, "lxml").text.strip()
        description = container.css(
            "div.ArticleLead").extract_first().strip()
        description = BeautifulSoup(description, "lxml").text.strip()
        paragraphs = container.css("div#ArticleContent p").extract()
        try:
            author = container.css("div#ArticleContent p span.bold").extract()[-1]
            author = BeautifulSoup(author, "lxml").text.strip()
        except:
            author = ''

        time = container.css('div.ArticleDateTime span.ArticleDate').extract_first()
        time = BeautifulSoup(time, 'lxml').text.strip()

        paragraphs = [BeautifulSoup(p, "lxml").text.strip() for p in paragraphs]

        if author in paragraphs:
            paragraphs.remove(author)
        if description in paragraphs:
            paragraphs.remove(description)

        page = response.url.split("/")[-1]
        id = page.split('.')[0].split('-')[-1]
        category = response.url.split('/')[3]
        filename = '{}/{}/{}.json'.format(self.name, category, id)

        directory_path = os.path.join(self.name, category)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        a = Article()
        a.url = response.url
        a.author = author
        a.title = title
        a.paragraphs = paragraphs
        a.description = description
        a.image_url = []
        a.time = self.format_time(time)

        print('Save: ', filename)
        with io.open(filename, 'w', encoding='utf8') as f:
            f.write(a.json())

        self.log('Save file %s' % filename, level=logging.DEBUG)

        # append history
        id = int(response.url.split('-')[-1].split('.')[0])
        self.crawled_ids.append(id)
        self.crawled_pages.append(response.url)

    def spider_closed(self, spider):
        """Summary

        Args:
            spider (TYPE): Description
        """
        self.log('Spider Closed')
        self.save_crawled_pages()

    def format_time(self, time):
        time = time.replace("\n", ' ')
        time = time.replace('&nbsp;', ' ')
        time = time.replace('      ', ' ')
        time = time.replace('      ', ' ')
        time = time.replace('  ', ' ')
        time = time.replace('  ', ' ')
        time = time.replace('  ', ' ')
        time = time.replace('  ', ' ')
        time = time.replace('  ', ' ')
        time = time.replace('  ', ' ')
        time = time.replace('  ', ' ')
        return time

    def load_crawled_pages(self):
        """Summary
        """
        if os.path.exists(self.crawled_history):
            with open(self.crawled_history) as f:
                pages = f.readlines()
            self.crawled_pages = [x.strip() for x in pages]
            self.crawled_ids = [int(x.split('-')[-1].split('.')[0]) for x in pages]

    def save_crawled_pages(self):
        """Summary
        """
        with open(self.crawled_history, 'w+') as f:
            for page in self.crawled_pages:
                f.writelines(page + '\n')
        self.log('save history %d' % len(self.crawled_pages), level=logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument('--start', default=515493, type=int)
parser.add_argument('--end', default=515495, type=int)
args = parser.parse_args()

process = CrawlerProcess()
process.crawl(NewsSpider, start=args.start, end=args.end)
process.start()






