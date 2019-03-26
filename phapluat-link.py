import scrapy
import os

from article import LinkSpider
from scrapy.crawler import CrawlerProcess


class PhapluatLinkSpider(LinkSpider):
    """Summary

    Attributes:
        name (str): Description
        topic (dict): Description
    """

    name = "phapluat"

    def start_requests(self):
        """Summary

        Yields:
            TYPE: Description
        """
        if not os.path.exists(self.name):
            os.mkdir(self.name)
        self.sub_categories = ['phap-luat/luat-va-doi']
        pattern = 'http://plo.vn/{}/'

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

        links = response.css("a.cms-link::attr(href)").extract()
        links = set(links)
        # links = set([x for x in links if len(x.split('/')) == 5])
        self.update_links(links)

        NEXT_PAGE_SELECTOR = 'span#ctl00_mainContent_ContentList1_pager a::attr(href)'

        next_page = response.css(NEXT_PAGE_SELECTOR).extract()
        if len(next_page) >= 1:
            next_page = 'https://plo.vn{}'.format(next_page[-1])
            yield scrapy.Request(
                url=next_page,
                callback=self.parse
            )


process = CrawlerProcess()
process.crawl(PhapluatLinkSpider)
process.start()
