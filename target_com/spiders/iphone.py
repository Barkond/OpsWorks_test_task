import json
import scrapy
from scrapy.http.headers import Headers
from target_com.items import IphoneItem

RENDER_HTML_URL = "http://127.0.0.1:8050/render.html"


class IphoneSpider(scrapy.Spider):
    name = 'iphone'
    start_urls = ['https://www.target.com/p/consumer-cellular-apple'
                  '-iphone-xr-64gb-black/-/A-81406260#lnk=sametab/']

    def start_requests(self):
        splash_headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9,ru;q=0.8,uk;q=0.7",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chro"
                         "mium\";v=\"96\", \"Google Chrome\";v=\"96\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWeb"'
                          '"Kit/537.36 (KHTML, like Gecko) "'
                          '"Chrome/96.0.4664.45 Safari/537.36'
        }
        for url in self.start_urls:
            body = json.dumps(
                {"url": url, "wait": 10, 'headers': splash_headers},
                sort_keys=True)
            headers = Headers({'Content-Type': 'application/json'})
            yield scrapy.Request(RENDER_HTML_URL, self.parse, method="POST",
                                 body=body, headers=headers)

    def parse(self, response):
        name = response.css('h1.Heading__Styled'
                            'Heading-sc-1mp23s9-0 > span::text').get()

        images = []
        for image in response.css('div.slideDeckPicture img'):
            img_url = image.css('::attr(src)').get()
            images.append(img_url)

        descr_raw = response.css('div.styles__StyledCol-sc'
                                 '-ct8kx6-0.jOZqCG.h-padding-l-default')
        description = descr_raw.css('div::text').get()

        highlights = []
        highlights_raw = response.css('ul.h-margin-h-tight')
        for highlight in highlights_raw.css('li'):
            highlight_text = highlight.css('span::text').get()
            highlights.append(highlight_text)

        sku = response.xpath(
            '//script[contains(text(), "x-api-key")]').re_first(
            r'"Product","tcin":"(.*?)"')

        pre_item = {
            'name': name,
            'description': description,
            'highlights': highlights,
            'sku': sku,
            'images': images
        }
        api_key = response.xpath('//script[contains(text(), "x-api-key")]').re_first(r'"x-api-key","value":"(.*?)"')
        print(sku)
        print(api_key)
        yield scrapy.Request(url='https://r2d2.target.com/ggc/Q&A/v1/question'
                                 '-answer?type=product&questionedId=81406260&'
                                 'page=0&size=10&sortBy=MOST_ANSWERS&key=c6b6'
                                 '8aaef0eac4df4931aae70500b7056531cb37&errorT'
                                 'ag=drax_domain_questions_api_error',
                             callback=self.parse_questions,
                             meta={'pre_item': pre_item,
                                   'api_key': api_key})

    def parse_questions(self, response):  # NOQA
        item = response.meta['pre_item']
        item['question'] = json.loads(response.text)['results'][0]['text']
        item['answer'] = json.loads(response.text)['results'][0]['answers'][0]['text']
        url = 'https://redsky.target.com/redsky_aggregations/v1/web/pdp_client_v1?'\
              f'key={response.meta["api_key"]}&tcin={response.meta["pre_item"]["sku"]}'\
              '&store_id=1338&pricing_store_id=1338&'\
              'latitude=50.490&longitude=30.420&state=30&zip=04070'
        print(url)
        yield scrapy.Request(url=url, callback=self.parse_api, meta={'pre_item': item})

    def parse_api(self, response):  # NOQA
        pre_item = response.meta['pre_item']
        api_data = json.loads(response.text)
        price = api_data['data']['product']['price']['current_retail']
        item = IphoneItem(**pre_item)
        item['price'] = price
        yield item
