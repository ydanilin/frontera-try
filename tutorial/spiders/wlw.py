# -*- coding: utf-8 -*-
from functools import partial
from itertools import chain
import scrapy
from scrapy.http import Request
from scrapy.http.response.html import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy import signals
from ..utils import filter_qparams, get_id_from_path


import logging
from scrapy.utils.log import configure_logging

configure_logging(install_root_handler=False)
logging.config.fileConfig('logging.conf')


class WlwSpider(scrapy.Spider):
    name = 'wlw'
    allowed_domains = ['wlw.de']
    # start_urls = ['https://www.wlw.de/de/firmen/tiefdruck']  # tiefdruck

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        spider.crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        return spider

    def __init__(self, *args, **kwargs):
        super(WlwSpider, self).__init__(*args, **kwargs)
        self.le_paging = LinkExtractor(
            restrict_xpaths=('//ul[@class="pagination"]/'
                             'li[not(@class)]/'
                             'a[text()[contains(.,"chste")]]')
        )
        allow = [r'.*\/firma\/.*',]
        self.le_items = LinkExtractor(allow=allow, unique=True)

    def spider_idle(self):
        self.log("Spider idle signal caught.")
        raise DontCloseSpider

    def parse(self, response):
        if not isinstance(response, HtmlResponse):
            return
        # find paging links
        paging_links = self.le_paging.extract_links(response)
        paging_requests = map(self.make_paging_request, paging_links)
        # find items
        items_links = self.le_items.extract_links(response)
        items_requests = map(self.make_item_request, items_links)
        
        yield from chain(paging_requests, items_requests)

    @staticmethod
    def make_paging_request(link):
        url, page_to = filter_qparams(['page'], 'retain', link.url)
        flight = {
            'dest': 'page',
            'to': page_to['page'],
        }
        r = Request(url)
        r.meta.update(flight=flight)
        return r

    @staticmethod
    def make_item_request(link):
        url, _ = filter_qparams([], 'retain', link.url)
        firma_id = get_id_from_path(url)
        flight = {
            'dest': 'item',
            'details': {'firma_id': firma_id}
        }
        r = Request(url)
        r.meta.update(flight=flight)
        return r
