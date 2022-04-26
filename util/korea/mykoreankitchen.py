import pandas as pd
import json
import requests
from lxml import html
import re
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua 
import multiprocessing as mp
#from pathos.multiprocessing import ProcessingPool as Pool #python package which enables multiprocessing on child classes
import time
import demjson
import random
import undetected_chromedriver.v2 as uc 

from  util.spider import Spider


class KoreanKitchen(Spider):

    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)


    def get_items_from_page(self, page_url):
        #add undetected chromedriver options
        options = uc.ChromeOptions()
        # options.headless=True
        # options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        driver.get(page_url)
        next_page_button = driver.find_element_by_xpath('//div[@class="wpupg-pagination-button"]')
        try:
            while (next_page_button):
                next_page_button.click()
                time.sleep(2)
        except:
            print('end of scrolling')
            pass

        doc = html.document_fromstring(driver.page_source)
        urls = doc.xpath(self.listing['items'])
        print(len(urls))
        driver.close() 
        return urls