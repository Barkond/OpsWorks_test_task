import scrapy


class IphoneItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    higlights = scrapy.Field()
    question = scrapy.Field()

