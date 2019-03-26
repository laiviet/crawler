import json
import scrapy
from scrapy import signals
import io


def formalize(str):
    str = str.replace('\n', ' ')
    str = str.replace('\r', ' ')
    str = str.replace('\t', ' ')
    str = str.replace('     ', ' ')
    str = str.replace('     ', ' ')
    str = str.replace('     ', ' ')
    str = str.replace('    ', ' ')
    str = str.replace('    ', ' ')
    str = str.replace('    ', ' ')
    str = str.replace('   ', ' ')
    str = str.replace('   ', ' ')
    str = str.replace('  ', ' ')
    str = str.replace('  ', ' ')
    return str


class Article(object):

    def __init__(self):
        super(Article, self).__init__()
        self.url = ''
        self.title = ''
        self.paragraphs = []
        self.description = ''
        self.author = ''
        self.time = None

    def clean(self):
        self.paragraphs = [formalize(p) for p in self.paragraphs]
        self.description = formalize(self.description)

    def json(self):
        obj = {'url': self.url,
               'title': self.title,
               'paragraph': self.paragraphs,
               'description': self.description,
               'author': self.author,
               'time': self.time}
        return json.dumps(obj, indent=4, ensure_ascii=False)


class LinkSpider(scrapy.Spider):
    """
    link dictionary:
        key: category
        value: set of links
    """
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
        assert cls.name, 'Spider has to have a name'
        spider = super(LinkSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed,
                                signal=signals.spider_closed)
        return spider

    def update_links(self, links, extractor=None):
        """

        :param links: iteratable of string
        :param extractor: function that extract category from link
        :return:
        """
        if extractor == None:
            extractor = lambda x: x.split('/')[3]

        for link in links:
            slashes = [1 for x in link if x == '/']
            if sum(slashes) < 4:
                continue

            category = extractor(link)
            if category not in self.links:
                self.links[category] = set()
            self.links[category].add(link)

    def spider_closed(self):
        """
        close and save links to file
        :return:
        """
        for category, links in self.links.items():
            path = '{}/{}.txt'.format(self.name, category)
            with io.open(path, 'a+', encoding='utf-8') as f:
                for link in links:
                    f.write(link + '\n')


class NewsSpider(scrapy.Spider):
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
        }
    }
