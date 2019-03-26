import scrapy
from scrapy import signals
import codecs
from bs4 import BeautifulSoup
import datetime
import calendar
import argparse
import os
from article import LinkSpider
from scrapy.crawler import CrawlerProcess


class VnexpressLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "vnepxress"

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """

        if not os.path.exists(self.name):
            os.mkdir(self.name)

        date_from = datetime.datetime(2019, 1, 31, 0, 0, 0)
        date_to = datetime.datetime(2019, 1, 31, 23, 59, 59)

        date_from_epoch = calendar.timegm(date_from.timetuple())
        date_to_epoch = calendar.timegm(date_to.timetuple())
        # 1001002: the gioi
        # 1002565: the thao,
        # 1001007: phap luat
        # 1002691: giai tri
        # 1003497: giao duc
        # 1001009: khoa hoc
        # 1001006: oto xe may
        # 1003159: kinh doanh
        # 1002592: so hoa
        # 1002966: gia dinh
        # 1003784: suc khoe

        # self.categories = {'thoi-su': 1001005,
        #                    'goc-nhin': 1003450,
        #                    'doi-song': 1002966,
        #                    'the-gioi': 1001002,
        #                    'the-thao': 1002565,
        #                    'phap-luat': 1001007,
        #                    'giai-tri': 1002691,
        #                    'giao-duc': 1003497,
        #                    'khoa-hoc': 1001009,
        #                    'xe': 1001006,
        #                    'kinh-doanh': 1003159,
        #                    'du-lich': 1003231,
        #                    'so-hoa': 1002592,
        #                    'gia-dinh': 1002966,
        #                    'suc-khoe': 1003750}

        # self.categories = {'thoi-su': 1001005}
        # self.categories = {'goc-nhin': 1003450}
        # self.categories = {'doi-song': 1002966}
        # self.categories = {'the-gioi': 1001002}
        # self.categories = {'the-thao': 1002565}
        # self.categories = {'phap-luat': 1001007}
        # self.categories = {'giai-tri': 1002691}
        # self.categories = {'giao-duc': 1003497}
        # self.categories = {'khoa-hoc': 1001009}
        # self.categories = {'xe': 1001006}
        #
        # self.categories = {'kinh-doanh': 1003159}
        # self.categories = {'du-lich': 1003231}
        # self.categories = {'so-hoa': 1002592}
        # self.categories = {'gia-dinh': 1002966}
        self.categories = {'suc-khoe': 1003750}

        self.categories_rev = {v: k for k, v in self.categories.items()}
        pattern = 'http://vnexpress.net/category/day/?cateid=%d&fromdate=%s&todate=%s'
        self.category = None

        for category_name, category_number in self.categories.items():
            url = pattern % (category_number, date_from_epoch, date_to_epoch)
            self.log(url)
            self.category = category_name
            yield scrapy.Request(url=url, callback=self.parse,
                                 meta={'category': category_name})

    def parse(self, response):
        """Summary

        Args:
            response (TYPE): Description

        Yields:
            TYPE: Description
        """
        links = response.css("article.list_news h3.title_news a::attr(href)").extract()

        self.update_links(links)

        NEXT_PAGE_SELECTOR = 'div.pagination  a.next::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        # self.log(next_page)
        if next_page:
            yield scrapy.Request(
                url=response.urljoin(next_page),
                callback=self.parse
            )

process = CrawlerProcess()
process.crawl(VnexpressLinkSpider)
process.start()
