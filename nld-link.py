import scrapy
from scrapy import signals
import codecs
from bs4 import BeautifulSoup
import datetime
import os
from article import LinkSpider
from scrapy.crawler import CrawlerProcess
import argparse


class NldLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "nld"

    def start_requests(self, **kwargs):
        """Summary

        Yields:
            TYPE: Description
        """
        if not os.path.exists(self.name):
            os.mkdir(self.name)

        date_from = datetime.date(2019, 1, 25)
        date_to = datetime.date(2019, 1, 31)

        diff = (date_to - date_from).days

        days = []

        for d in range(diff):
            today = date_from + datetime.timedelta(d)
            days.append((today.day, today.month, today.year))

        self.sub_categories = ['thoi-su',
                               'thoi-su/chinh-tri',
                               'thoi-su/xa-hoi',
                               'thoi-su/cau-chuyen-hom-nay',
                               'thoi-su/phong-su-but-ky',
                               'thoi-su-quoc-te'
                               ]
        self.sub_categories = [
            'thoi-su/chinh-tri'
        ]
        self.main_categories = [x.split('/')[0] for x in self.sub_categories]

        pattern = 'https://nld.com.vn/{}/xem-theo-ngay-{}-{}-{}.htm'

        for category in self.sub_categories:
            for d, m, y in days:
                if d < 10:
                    day = '0' + str(d)
                else:
                    day = str(d)
                if m < 10:
                    month = '0' + str(m)
                else:
                    month = str(m)
                url = pattern.format(category, day, month, y)
                self.log(url)
                # exit(0)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Summary

        Args:
            response (TYPE): Description

        Yields:
            TYPE: Description
        """
        links = response.css("div.box2 div.threaditem-bt a::attr(href)").extract()
        links = set(links)
        links = ['https://nld.com.vn' + x for x in links]
        self.update_links(links)


process = CrawlerProcess()
process.crawl(NldLinkSpider)
process.start()
