# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
import time
import re, json

from facebook.items import FacebookItem
from scrapy.loader import ItemLoader
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PathfinderSpider(scrapy.Spider):
    name = 'pathfinder'
    allowed_domains = ['facebook.com']
    start_urls = ['http://facebook.com/']

    def __init__(self, login, pswd, start_user, finish_user, *args, **kwargs):
        self.login = login
        self.pswd = pswd
        self.start_user = start_user
        self.finish_user = finish_user
        self.chrome = webdriver.Chrome()
        self.chrome.implicitly_wait(10)
        super().__init__(*args, *kwargs)

    def parse(self, response: HtmlResponse):
        self.chrome.get('https://www.facebook.com')

        login_element = self.chrome.find_element_by_xpath(
            '//input[@class = "inputtext login_form_input_box" and @type = "email"]')
        login_element.send_keys(self.login)

        pswd_element = self.chrome.find_element_by_xpath(
            '//input[@class = "inputtext login_form_input_box" and @type = "password"]')
        pswd_element.send_keys(self.pswd)

        input_btn = self.chrome.find_element_by_xpath('//label[@id = "loginbutton"]/input')
        input_btn.send_keys(Keys.ENTER)
        yield response.follow(self.start_user,
                              callback=self.parse_profile)

        yield response.follow(self.finish_user,
                              callback=self.parse_profile)

    def parse_profile(self, response: HtmlResponse):
        # self.chrome.get(response.url)
        if re.search(r'profile.php', response.url):
            current_user_id = response.url.split('=')[-1]
            self.chrome.get(f"https://m.facebook.com/profile.php?v=friends&id={current_user_id}")
        else:
            current_user_id = response.xpath('//meta[@property = "al:android:url"]/@content').extract_first().split('/')[-1]
            current_user_nickname = response.url.split('/')[-1]
            self.chrome.get(f"https://m.facebook.com/{current_user_nickname}/friends")
        time.sleep(3)
        print('Scrolling to bottom...')
        # Scroll to bottom
        while self.chrome.find_elements_by_css_selector('#m_more_friends'):
            self.chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        friends = list(map(lambda item: json.loads(item.get_attribute('data-store')).get('id') if item else None,
                 self.chrome.find_elements_by_xpath('//a[@class = "touchable right _58x3"]')))
        yield FacebookItem(user_id=int(current_user_id), friends=friends)
        for friend in friends:
            yield response.follow(f'{friend}',
                                  callback=self.parse_profile)


