import scrapy
import os

from article import LinkSpider
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess


class LaodongLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "laodong"

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        self.sub_categories = ['dinh-duong-am-thuc']
        pattern = 'https://laodong.vn/{}/'

        for category in self.sub_categories:
            url = pattern.format(category)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Summary

        Args:
            response (TYPE): Description

        Yields:
            TYPE: Description
        """

        links = response.css("a::attr(href)").extract()
        links = {x for x in links if x.endswith('.ldo')}
        links = {x for x in links if x.startswith('https://laodong.vn/')}
        self.update_links(links)

        load_more = response.css("div#load_more_btn_group").extract()
        if len(load_more) > 0:
            next_page = response.url + "?page=2"
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )

        panigation = response.css('ul.pagination li').extract()
        urls = response.css('ul.pagination li a::attr(href)').extract()

        next_idx = -1
        for idx, li in enumerate(panigation):
            if 'class=" active"' in li:
                next_idx = idx + 1
                break

        if next_idx > -1:
            yield scrapy.Request(
                url=urls[next_idx],
                callback=self.parse
            )


process = CrawlerProcess()
process.crawl(LaodongLinkSpider)
process.start()
