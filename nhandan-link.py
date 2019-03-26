import scrapy
from scrapy import signals
import codecs
import argparse
import os
from article import LinkSpider
from scrapy.crawler import CrawlerProcess


class NhandanLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "nhandan"

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        if not os.path.exists(self.name):
            os.mkdir(self.name)

        self.sub_categories = ['phapluat/van-ban-moi']
        self.main_categories = [x.split('/')[0] for x in self.sub_categories]

        pattern = 'http://nhandan.com.vn/{}'

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

        link_1 = response.css("div.hotnew-container a::attr(href)").extract()
        link_2 = response.css("div.dvs-container a::attr(href)").extract()
        links = {'http://nhandan.com.vn' + x for x in link_2 + link_1 if x}

        self.update_links(links)

        lis = response.css('ul.pagination  li').extract()
        next_page = response.css('ul.pagination  a::attr(href)').extract()

        next_idx = -1
        for idx, li in enumerate(lis):
            if 'class="active"' in li:
                next_idx = idx + 1
                break

        next_page = next_page[next_idx]

        # print(next_page)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )


process = CrawlerProcess()
process.crawl(NhandanLinkSpider)
process.start()
