import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hanabank.items import Article


class hanabankSpider(scrapy.Spider):
    name = 'hanabank'
    start_urls = ['https://www.hanabank.com/cont/news/news01/index.jsp']
    page = 1

    def parse(self, response):
        links = response.xpath('//ul[@class="news_list"]/li//a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1

            next_page = f'https://www.hanabank.com/cont/news/news01/index,1,list,{self.page}.jsp'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h4/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//td/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//td[@class="cont"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
