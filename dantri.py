# -*- coding: utf-8 -*-
"""

@author: Viet Lai
"""
import scrapy
import io
import os
import logging

from article import Article
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from os.path import join


class NewsSpider(scrapy.Spider):
    """Summary

    Attributes:
        crawled_history (str): Description
        crawled_pages (list): Description
        name (str): Description
    """

    name = "dantri"
    crawled_history = "history/{}.txt".format(name)
    crawled_pages = []

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
        return spider

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        self.load_crawled_pages()

        # get all text file in folder Links
        files = [x for x in os.listdir(self.link_directory) if x.endswith('.txt')]
        for file in files:
            file_name = os.path.join(self.link_directory, file)
            # self.log(file_name)
            #
            # read all links in each text file
            with open(file_name) as f:
                links = f.readlines()
            links = [x.strip() for x in links]

            # crawl data for each link
            base = os.path.basename(file_name)
            directory = os.path.splitext(base)[0]
            try:
                os.mkdir(join('dantri', directory))
            except:
                pass
            for link in links:
                page = link.split("/")[-1]
                if page not in self.crawled_pages:
                    yield scrapy.Request(url=link, callback=self.parse,
                                         meta={'directory': directory})
                    # break

    def parse(self, response):
        """Summary

        Args:
            response (TYPE): Description
        """
        container = response.css("div#ctl00_IDContent_ctl00_divContent")[0]
        title = container.css("h1").extract_first().strip()
        title = BeautifulSoup(title, "lxml").text.strip()

        description = container.css("h2").extract_first().strip()
        description = BeautifulSoup(description, "lxml").text.strip()

        time = container.css('div.box26 span.tt-capitalize').extract_first()
        time = BeautifulSoup(time, 'lxml').text.strip()

        paragraphs = container.css("div#divNewsContent p").extract()
        paragraphs = [x for x in paragraphs if '<strong>' not in x]
        paragraphs = [BeautifulSoup(p, "lxml").text.strip() for p in paragraphs]
        paragraphs = [x for x in paragraphs if len(x) > 0]

        author = container.css("div#divNewsContent p strong").extract()[-1]
        author = BeautifulSoup(author, "lxml").html.findAll(text=True, recursive=False)

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
        a.time = time

        print('Save: ', filename)
        with io.open(filename, 'w', encoding='utf8') as f:
            f.write(a.json())

        self.log('Saved: {}'.format(filename), level=logging.DEBUG)

        # append history
        self.crawled_pages.append(response.url)

    def spider_closed(self, spider):
        """Summary

        Args:
            spider (TYPE): Description
        """
        self.log('Spider Closed')
        self.save_crawled_pages()

    def load_crawled_pages(self):
        """Summary
        """
        if os.path.exists(self.crawled_history):
            with open(self.crawled_history) as f:
                pages = f.readlines()
            self.crawled_pages = [x.strip() for x in pages]

    def save_crawled_pages(self):
        """Summary
        """
        with open(self.crawled_history, 'w+') as f:
            for page in self.crawled_pages:
                f.writelines(page + '\n')
        print('Save history',len(self.crawled_pages))


process = CrawlerProcess()
process.crawl(NewsSpider)
process.start()
