import scrapy
import json
import requests
from scrapy.http import HtmlResponse
from datetime import datetime


class RewardsforjusticeNetSpider(scrapy.Spider):
    name = 'RWJST'
    allowed_domains = ['rewardsforjustice.net']
    start_urls = ['https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074',
                  'https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074&pagenum=2']

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_ITEMS': 150,
    }

    request_header = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest'
    }

    body = 'action=jet_engine_ajax&handler=get_listing&page_settings%5Bpost_id%5D=22076&page_settings%5Bqueried_id%5D=22076%7CWP_Post&page_settings%5Belement_id%5D=ddd7ae9&page_settings%5Bpage%5D=1&listing_type=elementor&isEditMode=false'

    cat_dictionary = {}

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parseLink,
                method="POST",
                body=self.body,
                headers=self.request_header
            )

    def clear_date(self, string):
        string = string.strip('\n\t')
        string = string.split(';')
        return string


    def convert_date(self, string):
        try:
            string = str(datetime.date(datetime.strptime(string.lstrip(), "%B %d, %Y")))
        except:
            return string
        return string


    def date_convert(self, date_str):
        if date_str is not None:
            return str(list(map(lambda x: self.convert_date(x), self.clear_date(date_str))))


    def parseLink(self, response):
        jsn = json.loads(response.text)
        resp = HtmlResponse(url=response.request.url, body=jsn['data']['html'], encoding='utf-8')
        links = resp.xpath("//a/@href").getall()
        catalogs =  resp.xpath("//div[@data-id='30c11ef']/div/h2/text()").getall()
        self.cat_dictionary.update ( dict(zip( links,catalogs)))
        yield from response.follow_all(links, self.parsePage)


    def parsePage(self, response):
        page = response.xpath("//body")
        page_url = response.request.url
        page_title = page.xpath("//div[@data-id='f2eae65']/div/h2/text()").get()
        page_about = page.xpath("//div[@data-id='52b1d20']/div/p").get()
        page_reward_amount = page.xpath("//div[@data-id='5e60756']/div/h2/text()").get()
        page_associated_organization = page.xpath("//div[@data-id='095ca34']/div/p/a/text()").get()
        page_associated_location = page.xpath("//div[@data-id='0fa6be9']/div/div/span/text()").get()
        page_images = page.xpath("//div[@id='gallery-1']/figure/div/picture/img/@src").get()
        page_date_of_birthday = self.date_convert(page.xpath("//div[@data-id='9a896ea']/div/text()").get())
        page_category = self.cat_dictionary[page_url]

        yield {
            'PageURL': page_url.strip() if page_url else "null",
            'Category': page_category.strip() if page_category else "null",
            'Title': page_title.strip() if page_title else "null",
            'RewardAmount': page_reward_amount.strip()[6:] if page_reward_amount else "null",
            'AssociatedOrganization': page_associated_organization.strip() if page_associated_organization else "null",
            'AssociatedLocation': page_associated_location.strip() if page_associated_location else "null",
            'About': page_about.strip() if page_about else "null",
            'Images': page_images.strip() if page_images else "null",
            'DateOfBirthday': page_date_of_birthday.strip('[]') if page_date_of_birthday else "null",
        }
