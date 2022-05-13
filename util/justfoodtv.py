# from selenium import webdriver 
# from selenium.webdriver.chrome.options import Options
import undetected_chromedriver.v2 as uc #only for starting the driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
import random
import requests
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua 
import json
import demjson
import multiprocessing as mp
import time

from  util.spider import Spider

class JustFood(Spider):
    
    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)


    def get_items_from_page(self, url):
        """Get all item urls from the current page listing

        Args:
            page_url (str): url of the page

        Returns:
           list: list containing the url of items in the current page
        """
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options)
        try:
            driver.get(url)
            xpath = '//div[@class="lsttitle"]' #wait till this element is there
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.refresh()
        except Exception as e:
            print(e)
            print('connection error for page: {}'.format(url))
            # return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            # 'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
        doc = html.document_fromstring(driver.page_source)
        
        driver.close() #close chromedriver
        try:
            urls = doc.xpath(self.listing['items'])
            #print('got items from url: ', page_url)
            if not urls:
                for r in range(5): #5 times retry
                    print('retrying... attempt {}'.format(r))
                    res2 = driver.get(url)
                    time.sleep(1)
                    doc2 = html.document_fromstring(res2.page_source)
                    urls = doc2.xpath(self.listing['items'])
                    if urls: 
                        break
            return urls

        except:
            #raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))
            print('Cannot open the menu url, url= {}'.format(url))
            return []



    