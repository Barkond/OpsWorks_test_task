import scrapy
from scrapy_splash import SplashRequest


class IphoneSpider(scrapy.Spider):
    name = 'iphone'

    def start_requests(self):
        url = ['https://www.target.com/p/consumer-cellular-apple-iphone-xr-64gb-black/-/A-81406260#lnk=sametab/'] # NOQA
        yield SplashRequest(url=url, callback=self.parse,
                            args={
                                'wait': 1
                            })

    def parse(self, response):
        pass
