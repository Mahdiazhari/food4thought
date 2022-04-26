#packages
import pandas as pd
import json
import requests
from random import randint
from lxml import html
import re
import time
import multiprocessing as mp
#from pathos.multiprocessing import ProcessingPool as Pool #python package which enables multiprocessing on child classes
import time
import demjson

#utilities
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua
from  util.spider import Spider


class RussianSpider(Spider): #inherit Spider Class

    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)

    def scrape_one_item(self,url):
        """To scrape one item from a given url

        Args:
            url (str): url of the item

        Returns:
            dict: dict of the item
        """
      
        session = requests.Session() 
        session = requests.Session() 
        #randomize user-agent in every request
        random_ua =  get_random_ua()
        header_template = self.header
        header_template['user-agent'] = random_ua
        session.headers.update(header_template)

        #add random time sleep for this website
        random_second = randint(2,4)
        time.sleep(random_second)

        #add home page url to the obtained item url if item url is not complete
        if self.main_page not in url:
            res = session.get(self.main_page + url)
        else:
            res = session.get(url)
        
        #default valuess
        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        if res.status_code == 200:
            try:
                #print(res.status_code)
                doc = html.document_fromstring(res.text)
                #set default values for variables
                

                #Name
                if self.check_normalize_space(self.attrs['name']):
                    name = doc.xpath(self.attrs['name'])
                else: name = doc.xpath(self.attrs['name'])[0]

                #Total Time
                if self.check_normalize_space(self.attrs['total_time']):
                    total_time = doc.xpath(self.attrs['total_time'])
                else:  total_time = doc.xpath(self.attrs['total_time'])[0]

                #ingredients
                ingredients = doc.xpath(self.attrs['ingredients'])
                clean_ingredients = []
                for ing in ingredients:
                    ing = ing.replace('\t','')
                    ing = ing.replace('\r','')
                    ing = ing.replace('\n','')
                    clean_ingredients.append(ing)

                #print(clean_ingredients)
                #ingredients = ''.join(clean_ingredients)
                #ingredients = ingredients.strip()
                # ingredient_str = ''
                # for ing in ingredients:
                #     if  ' ' not in str(ing):
                #         ingredient_str += ing

                ingredients = list(filter(None, clean_ingredients))
                

                #instructions
                instructions = doc.xpath(self.attrs['instructions'])
                #print(instructions)
                #instructions= ''.join(instructions)
                
                # instructions_str = ''
                # for ins in instructions:
                #     if  ' ' not in str(ins): 
                #         instructions_str += ins
                # instructions = instructions_str

                # if self.check_normalize_space(self.attrs['instructions']):
                #     instructions = doc.xpath(self.attrs['instructions'])
                # else:  instructions = doc.xpath(self.attrs['instructions'])[0]
            
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
                print(e)
                print('something is wrong for item: {}'.format(url)) 
                raise Exception(e)
            #     return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            # 'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}

        else:
            print('Cannot open one recipe url, status code = {}, url = {}'.format(res.status_code, url))
            raise Exception('Cannot open one menu url, status code = {}, url = {}'.format(res.status_code, url))
            # return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            # 'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
        
    # def start_scrape(self, max_pages=100, multithread=True):
    #     """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
    #     Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

    #      Args:
    #         max_pages (int): maximum number of pages to scrape, default =100 

    #     Returns:
    #         list: list containing the url of items for all seeds for all pages
    #     """

    #     COLUMN_NAMES = ['name','ingredients', 'total_time','instructions', 'servings','category','prep_time','cook_time']
    #     all_items = []
    #     try:
    #         for seed_url in self.seeds:
    #             if self.listing['next']['type'] == 'url':
    #                 for i in range(max_pages):
    #                     listing_items = []
    #                     page_url = seed_url + self.listing['next']['next_page_str'].format(i+1)
    #                     print('spider is scraping page: {}'.format(i+1))
    #                     #print('spider is scraping url: ', page_url)
    #                     listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
    #                     if not listing_items:
    #                         break #last page
    #                     if multithread: 
    #                         #pool = Pool() #initialize Pathos multiprocessing pool
    #                         pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
    #                         results  = pool.map(self.scrape_one_item, [url for url in listing_items])
    #                         print('scraping - multithreaded, n items: ', len(listing_items))
    #                         pool.close() #close the multiprocessing  pool
    #                     else:
    #                         results = []
    #                         for item_url in listing_items:
    #                             item = self.scrape_one_item(item_url)
    #                             results.append(item)
                                                
    #                     all_items += results

    #                     # for item_url in listing_items:
    #                     #     item = self.scrape_one_item(item_url)

    #                         #item_df = pd.DataFrame([item], columns=item.keys())
    #                         #df = pd.concat([df,item_df], ignore_index=True)
    #             # 
    #             if self.listing['next']['type'] == 'custom_modify_url':
    #                 for i in range(max_pages):
    #                     listing_items = []
    #                     page_url = seed_url.format(i+1)
    #                     print('spider is scraping page: {}'.format(i+1))
    #                     #print('spider is scraping url: ', page_url)
    #                     listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
    #                     if not listing_items:
    #                         break #last page
    #                     if multithread: 
    #                         #pool = Pool() #initialize Pathos multiprocessing pool
    #                         pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
    #                         results  = pool.map(self.scrape_one_item, [url for url in listing_items])
    #                         print('scraping - multithreaded, n items: ', len(listing_items))
    #                         pool.close() #close the multiprocessing  pool
    #                     else:
    #                         results = []
    #                         for item_url in listing_items:
    #                             item = self.scrape_one_item(item_url)
    #                             results.append(item)
                                                
    #                     all_items += results
       
    #         return all_items

    #     except Exception as e:
    #         print(e)
    #         return all_items
    
    def get_items_from_page(self, page_url):
        """Get all item urls from the current page listing

        Args:
            page_url (str): url of the page

        Returns:
           list: list containing the url of items in the current page
        """
        session = requests.Session() 
        #randomize user-agent in every request
        random_ua =  get_random_ua()
        header_template = self.header
        header_template['user-agent'] = random_ua
        session.headers.update(header_template)
        res = session.get(page_url)
        if res.status_code == 200:
            doc = html.document_fromstring(res.text)
            urls = doc.xpath(self.listing['items'])
            #print('got items from url: ', page_url)
            return urls
        else:
            #raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))
            print('Cannot open the menu url, status code = {}, url= {}'.format(res.status_code, page_url))
            return []
