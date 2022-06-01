from lxml import html
import random
import requests
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua 
import json
import demjson
import multiprocessing as mp
import time
from selenium import webdriver
from  util.spider import Spider


class AfrikCuisine(Spider):
    
    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)


    def get_items_from_page(self, page_url):
        #add undetected chromedriver options
        #options = uc.ChromeOptions()    
        # options.headless=True
        # options.add_argument('--headless')
        driver = webdriver.Chrome()
        print('started chromedriver...')
        driver.get(page_url)
        urls = []
        doc = html.document_fromstring(driver.page_source)
        urls_1 = doc.xpath(self.listing['items'])
        urls = urls + urls_1
        print('found this much items: ', len(urls))
        #next_page_button = driver.find_element_by_xpath('//a[@class="lien_pagination"]')
        # try:
        #     while (next_page_button):
        #         next_page_button.click()
        #         doc = html.document_fromstring(driver.page_source)
        #         urls_2 = doc.xpath(self.listing['items'])
        #         urls = urls + urls_2
        #         print('found this much items: ', len(urls))
        #         time.sleep(5)
        # except:
        #     print('end of scrolling')
        #     pass
        print('found this much items in the end: ', len(urls))
        print(urls)
        driver.close() 
        return urls
