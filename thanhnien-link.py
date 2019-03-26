import scrapy
import os

from article import LinkSpider
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess


class ThanhnienLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "thanhnien"

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        self.sub_categories = ['tai-chinh-kinh-doanh',
                               ]
        pattern = 'https://thanhnien.vn/{}/'

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

        links = response.css("a.story__title::attr(href)").extract()
        links = {x for x in links if x.endswith('.html')}
        links = {'https://thanhnien.vn' + x for x in links if x[0] == '/'}
        self.update_links(links)

        panigation = response.css('nav#paging li').extract()
        urls = response.css('nav#paging a::attr(href)').extract()

        next_idx = -1
        for idx, li in enumerate(panigation):
            if 'class="active"' in li:
                next_idx = idx
                break

        if next_idx > -1:
            yield scrapy.Request(
                url='https://thanhnien.vn' + urls[next_idx],
                callback=self.parse
            )


process = CrawlerProcess()
process.crawl(ThanhnienLinkSpider)
process.start()
