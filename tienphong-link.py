import scrapy
import os

from article import LinkSpider
from scrapy.crawler import CrawlerProcess


class TienphongLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "tienphong"

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        self.sub_categories = ['cau-chuyen-van-hoa']
        pattern = 'http://tienphong.vn/{}/'

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

        links = response.css("div.abc-column article a::attr(href)").extract()
        links = set([x for x in links if len(x.split('/')) == 5])
        self.update_links(links)

        NEXT_PAGE_SELECTOR = 'a#ctl00_mainContent_ContentList1_pager_nextControl::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract()
        assert len(next_page) == 1, "Please check next page, len={}".format(len(next_page))
        if len(next_page) == 1:
            next_page = 'https://tienphong.vn{}'.format(next_page[0])
            print(next_page)
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )


process = CrawlerProcess()
process.crawl(TienphongLinkSpider)
process.start()
