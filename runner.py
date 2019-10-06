import os
from os.path import join, dirname
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from facebook import settings
from facebook.spiders.pathfinder import PathfinderSpider
do_env = join(dirname(__file__), '.env')
load_dotenv(do_env)

INST_LOGIN = os.getenv('INST_LOGIN')
INST_PWD = os.getenv('INST_PASSWORD')

FACEBOOK_LOGIN = os.getenv('FACEBOOK_LOGIN')
FACEBOOK_PASSWORD = os.getenv('FACEBOOK_PASSWORD')

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(PathfinderSpider, FACEBOOK_LOGIN, FACEBOOK_PASSWORD, '100001826292284', '1059430706')
    process.start()
