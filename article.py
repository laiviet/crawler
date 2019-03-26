import json
import scrapy
from scrapy import signals
import io


class Article(object):

    def __init__(self):
        super(Article, self).__init__()
        self.url = ''
        self.title = ''
        self.paragraphs = []
        self.image_url = []
        self.description = ''
        self.author = ''
        self.time = None

    def json(self):
        obj = {'url': self.url,
               'title': self.title,
               'paragraph': self.paragraphs,
               'description': self.description,
               'author': self.author,
               'image_url': self.image_url,
               'time': self.time}
        return json.dumps(obj, indent=4, ensure_ascii=False)


class LinkSpider(scrapy.Spider):
    links = dict()

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
        spider = super(LinkSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        return spider

    def update_links(self, links, extractor=None):
        if extractor == None:
            extractor = lambda x: x.split('/')[3]

        # print(links)
        for link in links:
            slashes = [1 for x in link if x == '/']
            if sum(slashes) < 4:
                continue

            category = extractor(link)
            if category not in self.links:
                self.links[category] = set()
            self.links[category].add(link)

    def spider_closed(self):
        assert self.name, 'Spider has to have a name'

        for category, links in self.links.items():
            path = '{}/{}.txt'.format(self.name, category)
            with io.open(path, 'a+', encoding='utf-8') as f:
                for link in links:
                    f.write(link + '\n')
