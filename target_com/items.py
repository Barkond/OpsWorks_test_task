import scrapy


class IphoneItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    highlights = scrapy.Field()
    question = scrapy.Field()
    answer = scrapy.Field()
    sku = scrapy.Field()

