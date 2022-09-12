from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.utils.project import get_project_settings

from RWJST.spiders.rewardsforjustice_net import RewardsforjusticeNetSpider
from datetime import datetime


settings = get_project_settings()
process = CrawlerProcess(settings)
local_date_time = datetime.today().strftime("%Y%m%d_%H%M%S")
RewardsforjusticeNetSpider.name
reward_crawler = Crawler(
    RewardsforjusticeNetSpider,
    settings={
        **settings,
        "FEEDS": {
            str(RewardsforjusticeNetSpider.name) + "_" + str(local_date_time)+".json": {"format": "json"},
            str(RewardsforjusticeNetSpider.name) + "_" + str(local_date_time)+".xlsx": {"format": "xlsx"},
        },
    },
)

process.crawl(reward_crawler, tag="reward")

process.start()