import pandas as pd
import json
import requests
from lxml import html
import re
from util.http_utility import get_http_headers
import multiprocessing as mp
import time

class Spider:
    """Scraper Spider class for scraping recipes from countries. 

    Args:
        main_page (str): string containing the main url/homepage of the website
        seeds (list): list containing url of seed(s) (url categories of recipes, if separated)
        listing (dict): dictionary containing next and item list xpaths 
        attrs (dict): dictionary containing xpaths of the attributes to scrape
        headers (dict): dictionary of custom header if the website needs custom headers
    """
    def __init__(self, main_page, seeds, listing, attrs, header=None):
        self.main_page = main_page
        self.seeds = seeds
        self.listing = listing
        self.attrs = attrs
        if header:
            self.header=header #if website needs a custom header
        else:
            self.header = get_http_headers()


    def check_normalize_space(self,xpath):
        if 'normalize-space' in xpath:
            return True
        else: return False


    def scrape_one_item(self,url):
        """To scrape one item from a given url

        Args:
            url (str): url of the item

        Returns:
            dict: dict of the item
        """
        session = requests.Session() 
        session.headers.update(self.header)

        #add home page url to the obtained item url if item url is not complete
        if self.main_page not in url:
            res = session.get(self.main_page + url)
        else:
            res = session.get(url)

        if res.status_code == 200:
            try:
                #print(res.status_code)
                doc = html.document_fromstring(res.text)
                #set default values for variables
                name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

                #Name
                if self.check_normalize_space(self.attrs['name']):
                    name = doc.xpath(self.attrs['name'])
                else: name = doc.xpath(self.attrs['name'])[0]

                #Total Time
                if self.check_normalize_space(self.attrs['total_time']):
                    total_time = doc.xpath(self.attrs['total_time'])
                else:  total_time = doc.xpath(self.attrs['total_time'])[0]

                #ingredients
                if self.check_normalize_space(self.attrs['ingredients']):
                    ingredients = doc.xpath(self.attrs['ingredients'])
                else: ingredients = doc.xpath(self.attrs['ingredients'])[0]

                #instructions
                if self.check_normalize_space(self.attrs['instructions']):
                    instructions = doc.xpath(self.attrs['instructions'])
                else:  instructions = doc.xpath(self.attrs['instructions'])[0]

                #servings
                if self.attrs['servings']:
                    if self.check_normalize_space(self.attrs['servings']):
                        servings = doc.xpath(self.attrs['servings'])
                    else: servings = doc.xpath(self.attrs['servings'])[0]

                #category
                if self.attrs['category']:
                    if self.check_normalize_space(self.attrs['category']):
                        category = doc.xpath(self.attrs['category'])
                    else: category = doc.xpath(self.attrs['category'])[0]

                #prep time
                if self.attrs['prep_time']:
                    if self.check_normalize_space(self.attrs['prep_time']):
                        prep_time = doc.xpath(self.attrs['prep_time'])
                    else: prep_time = doc.xpath(self.attrs['prep_time'])[0]
                
                #cooking time
                if self.attrs['cook_time']:
                    if self.check_normalize_space(self.attrs['cook_time']):
                        cook_time = doc.xpath(self.attrs['cook_time'])
                    else: cook_time = doc.xpath(self.attrs['cook_time'])[0]

                return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
                'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
            except Exception as e:
                print('exception: ', e)
                raise Exception('something is wrong for item: {}'.format(url)) from e


        else:
            raise Exception('Cannot open one menu url, status code = {}'.format(res.status_code))

    
    # attrs = {
    #     'name':         '//meta[@property="og:title"]/@content',
    #     'ingredients':  '//meta[@itemprop="recipeIngredient"]/@content',
    #     'total_time':   '//meta[@itemprop="totalTime"]/@content',
    #     'instructions': '//meta[@itemprop="recipeInstructions"]/@content',
    #     'servings':     '//meta[@itemprop="recipeYield"]/@content',
    #     'category':     '//meta[@itemprop="recipeCategory"]/@content',
    #     'prep_time':    '',
    #     'cook_time':    '',
    # }

    # listing={'items': '//div[@class="contentS"]//a/@href', 'next': { 'next_page_str': '?p={}', 'type': 'url'}}
    # seeds = ['https://www.bucataras.ro/retete-traditionale/romania/']

    

    def start_scrape(self, max_pages=100, multithread=True):
        """Get all recipe items from the seeds given. Can choose to enable multithreading.
        Multithreading is used to immediately scrape all menu items from a list of menu urls, but becareful for blockers.

         Args:
            max_pages (int): maximum number of pages to scrape

        Returns:
            list: list containing the url of items for all seeds for all pages
        """

        COLUMN_NAMES = ['name','ingredients', 'total_time','instructions', 'servings','category','prep_time','cook_time']
       
        all_items = []
        try:
            for seed_url in self.seeds:
                # listing_items = []
                if self.listing['next']['type'] == 'url':
                    for i in range(max_pages):
                        page_url = seed_url + self.listing['next']['next_page_str'].format(i+1)
                        print('spider is scraping page: {}'.format(i+1))
                        listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
                        if multithread: 
                            pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
                            results  = pool.map(self.scrape_one_item, [url for url in listing_items])
                            pool.close() #close the multithreading  pool
                        else:
                            results = []
                            for item_url in listing_items:
                                item = self.scrape_one_item(item_url)
                                results.append(item)
                                                    
                        all_items += results

                        # for item_url in listing_items:
                        #     item = self.scrape_one_item(item_url)

                            #item_df = pd.DataFrame([item], columns=item.keys())
                            #df = pd.concat([df,item_df], ignore_index=True)            
            return all_items
        except Exception as e:
            print(e)
            return all_items
    
    def get_items_from_page(self, page_url):
        """Get all item urls from the current page listing

        Args:
            page_url (str): url of the page

        Returns:
           list: list containing the url of items in the current page
        """
        session = requests.Session() 
        session.headers.update(self.header)
        res = session.get(page_url)
        if res.status_code == 200:
            doc = html.document_fromstring(res.text)
            urls = doc.xpath(self.listing['items'])
            #print('these are the urls: ', urls)
            return urls
        else:
            raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))
        




