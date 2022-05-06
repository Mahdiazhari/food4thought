# from selenium import webdriver 
# from selenium.webdriver.chrome.options import Options
import undetected_chromedriver.v2 as uc
from lxml import html
import random
import requests
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua 
import json
import demjson
import multiprocessing as mp
import time
import urllib.parse #used to encode url encode any string

from  util.spider import Spider

class Food24(Spider):

    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)

    def start_scrape(self, max_pages=100, multithread=True):
        """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
        Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

         Args:
            max_pages (int): maximum number of pages to scrape, default =100 

        Returns:
            list: list containing the url of items for all seeds for all pages
        """

        POST_URL = 'https://www.food24.com/?ajax-request=jnews'
        all_items = []
        #try:
        for seed_url in self.seeds: #for this recipe website, the seeds will contain the payloads
            sample_payload = """
            lang=en_US&action=jnews_module_ajax_jnews_block_3&module=true&data[filter]=0&data[filter_type]=all&data[current_page]={current_page}&data[attribute][post_type]=recipe&data[attribute][categories]=549
            """

            #payload = """&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=حساء&term_slug=%d8%ad%d8%b3%d8%a7%d8%a1&ingredient_id=0&featured_id2=0&featured_id=182902&pageNumber=15&maxPages=37&action=more_post_ajax"""
            max_page = 166
            print('max page: ', max_page)
            for i in range(max_page):
                payload = seed_url.format(current_page=i+1)
                listing_items = []
                print('spider is scraping page: {}'.format(i+1))
                #print('spider is scraping url: ', page_url)
                session = requests.Session() 
                #randomize user-agent in every POST request
                random_ua =  get_random_ua()
                header_template = self.header
                header_template['user-agent'] = random_ua
                session.headers.update(header_template)
                
                res = session.post(POST_URL, data=payload,headers=self.header)
                if res.status_code == 200:
                    try:
                        #print(res.text)
                        response_json = json.loads(res.text)
                        html_doc = response_json.get('content')
                        doc = html.document_fromstring(html_doc)

                        #extract item urls from listing page
                        items_xpath = '//h3[@class="jeg_post_title"]//a/@href'
                        urls = doc.xpath(items_xpath)

                        #print(urls)
                        print('amount of urls we got: ', len(urls))
                        listing_items = urls
                    except:
                        print('doc is probably empty')
                else:
                    print('failed')
                    print(res.status_code)
                listing_items = list(set(listing_items)) #convert to set to remove duplicate urls
                if not listing_items:
                    break #last page
                if multithread: 
                    #pool = Pool() #initialize Pathos multiprocessing pool
                    pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
                    results  = pool.map(self.scrape_one_item, [url for url in listing_items])
                    print('scraping - multithreaded, n items: ', len(listing_items))
                    pool.close() #close the multiprocessing  pool
                else:
                    results = []
                    for item_url in listing_items:
                        item = self.scrape_one_item(item_url)
                        results.append(item)
                                        
                all_items += results
        

        return all_items
   