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
import undetected_chromedriver.v2 as uc 

from  util.spider import Spider


class MaldivesCook(Spider):
    
    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)

    def get_items_from_page(self, page_url):
        #add undetected chromedriver options
        options = uc.ChromeOptions()    
        # options.headless=True
        # options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        driver.get(page_url)
        next_page_button = driver.find_element_by_xpath('//div[@class="cooked-pages-load-wrap cooked-load-more-button"]')
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

    # def start_scrape(self, max_pages=100, multithread=True):
    #     """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
    #     Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

    #      Args:
    #         max_pages (int): maximum number of pages to scrape, default =100 

    #     Returns:
    #         list: list containing the url of items for all seeds for all pages
    #     """

    #     POST_URL = 'https://maldivescook.com/wp-admin/admin-ajax.php'
    #     all_items = []
    #     #try:
    #     for seed_url in self.seeds: #for this recipe website, the seeds will contain the payloads
    #         sample_payload = """

    #         action=cooked_loadmore&atts%5Bcategory%5D=false&atts%5Border%5D=false&atts%5Borderby%5D=false&atts%5Bshow%5D=false&atts%5Bsearch%5D=true&atts%5Bpagination%5D=true&atts%5Bcolumns%5D=4&atts%5Blayout%5D=modern&atts%5Bauthor%5D=&atts%5Bcompact%5D=false&atts%5Bhide_browse%5D=false&atts%5Bhide_sorting%5D=false&atts%5Bexclude%5D=false&atts%5Binline_browse%5D=false&atts%5Bcuisine%5D=false&atts%5Bcooking-method%5D=false&atts%5Btag%5D=false&recipe_args=a%3A6%3A%7Bs%3A5%3A%22paged%22%3Bi%3A1%3Bs%3A9%3A%22post_type%22%3Bs%3A9%3A%22cp_recipe%22%3Bs%3A14%3A%22posts_per_page%22%3Bs%3A2%3A%2212%22%3Bs%3A11%3A%22post_status%22%3Bs%3A7%3A%22publish%22%3Bs%3A7%3A%22orderby%22%3Ba%3A1%3A%7Bs%3A6%3A%22rating%22%3Bs%3A4%3A%22desc%22%3B%7Ds%3A10%3A%22meta_query%22%3Ba%3A5%3A%7Bs%3A8%3A%22relation%22%3Bs%3A3%3A%22AND%22%3Bs%3A6%3A%22rating%22%3Ba%3A3%3A%7Bs%3A3%3A%22key%22%3Bs%3A14%3A%22_recipe_rating%22%3Bs%3A5%3A%22value%22%3Bs%3A1%3A%221%22%3Bs%3A7%3A%22compare%22%3Bs%3A2%3A%22%3E%3D%22%3B%7Ds%3A13%3A%22rating_exists%22%3Ba%3A2%3A%7Bs%3A3%3A%22key%22%3Bs%3A14%3A%22_recipe_rating%22%3Bs%3A7%3A%22compare%22%3Bs%3A6%3A%22EXISTS%22%3B%7Di%3A0%3Ba%3A3%3A%7Bs%3A8%3A%22relation%22%3Bs%3A2%3A%22OR%22%3Bs%3A10%3A%22draft_null%22%3Ba%3A2%3A%7Bs%3A3%3A%22key%22%3Bs%3A13%3A%22_recipe_draft%22%3Bs%3A7%3A%22compare%22%3Bs%3A10%3A%22NOT+EXISTS%22%3B%7Ds%3A10%3A%22draft_zero%22%3Ba%3A3%3A%7Bs%3A3%3A%22key%22%3Bs%3A13%3A%22_recipe_draft%22%3Bs%3A7%3A%22compare%22%3Bs%3A2%3A%22!%3D%22%3Bs%3A5%3A%22value%22%3Bi%3A1%3B%7D%7Di%3A1%3Ba%3A3%3A%7Bs%3A8%3A%22relation%22%3Bs%3A2%3A%22OR%22%3Bs%3A12%3A%22pending_null%22%3Ba%3A2%3A%7Bs%3A3%3A%22key%22%3Bs%3A15%3A%22_recipe_pending%22%3Bs%3A7%3A%22compare%22%3Bs%3A10%3A%22NOT+EXISTS%22%3B%7Ds%3A12%3A%22pending_zero%22%3Ba%3A3%3A%7Bs%3A3%3A%22key%22%3Bs%3A15%3A%22_recipe_pending%22%3Bs%3A7%3A%22compare%22%3Bs%3A2%3A%22!%3D%22%3Bs%3A5%3A%22value%22%3Bi%3A1%3B%7D%7D%7D%7D&page={current_page}&is_own_profile=            
            
    #         """
    #         #payload = """&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=حساء&term_slug=%d8%ad%d8%b3%d8%a7%d8%a1&ingredient_id=0&featured_id2=0&featured_id=182902&pageNumber=15&maxPages=37&action=more_post_ajax"""
    #         max_page = 5
    #         print('max page: ', max_page)
    #         for i in range(1, max_page):
    #             payload = seed_url.format(current_page=i+1)
    #             listing_items = []
    #             print('spider is scraping page: {}'.format(i+1))
    #             #print('spider is scraping url: ', page_url)
    #             session = requests.Session() 
    #             #randomize user-agent in every POST request
    #             # random_ua =  get_random_ua()
    #             # header_template = self.header
    #             # header_template['user-agent'] = random_ua
    #             # session.headers.update(header_template)
                
    #             res = session.post(POST_URL, data=payload,headers=self.header)
    #             if res.status_code == 200:
    #                 try:
    #                     #print(res.text)
    #                     response_json = json.loads(res.text)
    #                     html_doc = response_json.get('content')
    #                     doc = html.document_fromstring(html_doc)

    #                     #extract item urls from listing page
    #                     items_xpath = self.listing['items']
    #                     urls = doc.xpath(items_xpath)

    #                     #print(urls)
    #                     print('amount of urls we got: ', len(urls))
    #                     listing_items = urls
    #                 except Exception as e:
    #                     print(e)
    #                     print('doc is probably empty')
    #             else:
    #                 print('failed')
    #                 print(res.status_code)
    #             listing_items = list(set(listing_items)) #convert to set to remove duplicate urls
    #             if not listing_items:
    #                 break #last page
    #             if multithread: 
    #                 #pool = Pool() #initialize Pathos multiprocessing pool
    #                 pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
    #                 results  = pool.map(self.scrape_one_item, [url for url in listing_items])
    #                 print('scraping - multithreaded, n items: ', len(listing_items))
    #                 pool.close() #close the multiprocessing  pool
    #             else:
    #                 results = []
    #                 for item_url in listing_items:
    #                     item = self.scrape_one_item(item_url)
    #                     results.append(item)
                                        
    #             all_items += results
        

    #     return all_items