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

from  util.spider import Spider


class Govtach(Spider):
    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)
    
    def check_normalize_space(self,xpath):
        if 'normalize-space' in xpath:
            return True
        else: return False

    def start_scrape(self, max_pages=100, multithread=True):
        """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
        Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

         Args:
            max_pages (int): maximum number of pages to scrape, default =100 

        Returns:
            list: list containing the url of items for all seeds for all pages
        """

        COLUMN_NAMES = ['name','ingredients', 'total_time','instructions', 'servings','category','prep_time','cook_time']
        all_items = []
        #try:
        for seed_url in self.seeds:
            if self.listing['next']['type'] == 'random_pages':
                max_items  = self.listing['next']['max_items'] 
                item_per_page = self.listing['next']['items_per_page']
                max_pages = self.listing['next']['max_pages']
                n_pages = int(max_items/item_per_page)
                random_pages = random.sample(range(1, max_pages), n_pages)
                print('n of pages scraper will scrape: ', len(random_pages))
                for i in random_pages:
                    listing_items = []
                    page_url = seed_url.format(page=i)
                    print('spider is scraping page: {}'.format(i))
                    #print('spider is scraping url: ', page_url)
                    listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
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

        # except Exception as e:
        #     print(e)
        #     return all_items
    
