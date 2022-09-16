import scrapy
import json
import requests
from scrapy.http import HtmlResponse
import datetime


class RewardsforjusticeNetSpider(scrapy.Spider):
    name = 'RWJST'
    allowed_domains = ['rewardsforjustice.net']
    start_urls = ['https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1074',]
    #'https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074&pagenum=2'


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
                callback=self.page_counter,
                method="POST",
                body=self.body,
                headers=self.request_header
            )

    def clear_date(self, string):
        string = string.strip('\n\t').split(';')
        return string


    def convert_date(self, string):
        try:
            string = str(datetime.datetime.date(datetime.datetime.strptime(string.lstrip(),"%B %d, %Y")))
        except:
            return string
        return string


    def date_convert(self, date_str):
        if date_str is not None:
            return str(list(map(lambda x: self.convert_date(x), self.clear_date(date_str))))


    def page_counter(self, response):
        jsn = json.loads(response.text)
        current_page = jsn['data']['filters_data']['props']['rewards-grid']['page']
        max_page = jsn['data']['filters_data']['props']['rewards-grid']['max_num_pages']
        found_posts = jsn['data']['filters_data']['props']['rewards-grid']['found_posts']
        print("current_page :" + str(current_page) + "  "+ "max_page: "+ str(max_page)  + "  " + "found_posts: " + str(found_posts))
        for count in range(1, max_page+1):
            yield scrapy.Request(
                self.start_urls[0]+"&pagenum="+str(count),
                callback=self.parse_link,
                method="POST",
                body=self.body,
                headers=self.request_header
            )


    def parse_link(self, response):
        jsn = json.loads(response.text)
        resp = HtmlResponse(url=response.request.url, body=jsn['data']['html'], encoding='utf-8')
        links = resp.xpath("//a/@href").getall()
        catalogs =  resp.xpath("//div[@data-id='30c11ef']/div/h2/text()").getall()
        self.cat_dictionary.update ( dict(zip( links,catalogs)))
        yield from response.follow_all(links, self.parse_page)

    class Page(scrapy.Item):
        page_url = scrapy.Field()
        page_category = scrapy.Field()
        page_title = scrapy.Field()
        page_about = scrapy.Field()
        page_reward_amount = scrapy.Field()
        page_associated_organization = scrapy.Field()
        page_associated_location = scrapy.Field()
        page_images = scrapy.Field()
        page_date_of_birthday = scrapy.Field()


    def parse_page(self, response):
        #page = response.xpath("//body")
        page = self.Page()
        page_url = response.request.url
        page_title = response.xpath("//*[@id='hero-col']/div/div[1]/div/h2").get()
        page_about = response.xpath("//*[@id='reward-about']/div/div[2]/div/p").getall()
        page_reward_amount = response.xpath("//*[@id='reward-box']/div/div[2]/div/h2/text()").get()
        page_associated_organization = response.xpath("//*[@id='Rewards-Organizations-Links']/div/p/a/text()").get()
        page_associated_location = response.xpath("///*[@id='reward-fields']/div/div[7]/div/div/span/text()").extract() ###
        #page_images = response.xpath("//*[@id='gallery-1']/figure[1]/div/picture/img/@src").getall()
        page_images = response.xpath("//*[@id='gallery-1']/figure[1]/@src").getall()
        print(page_images)
        page_date_of_birthday = self.date_convert(response.xpath("//h2[contains(text(), 'Date of Birth:')]/../../following-sibling::div/div/text()").get())
        page_category = self.cat_dictionary[page_url]



       # page['page_url'] =  page_url.strip() if page_url else None,
       # page['page_title'] = page_title.strip() if page_title else None,
       # page['page_about'] = page_about.strip() if page_about else None,
       # page['page_reward_amount'] =page_reward_amount.strip()[6:] if page_reward_amount else None,
       # page['page_associated_organization'] = page_associated_organization.strip() if page_associated_organization else None,
       # page['page_associated_location'] = page_associated_location.strip() if page_associated_location else None,
       # page['page_images'] = page_images.strip() if page_images else None,
       # page['page_date_of_birthday'] = page_date_of_birthday.strip('[]') if page_date_of_birthday else None,
       # page['page_category'] = page_category.strip() if page_category else None

       # yield page
