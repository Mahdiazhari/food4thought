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

class Coolinarika: #inherit Spider Class

    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None):
        self.main_page = main_page
        self.seeds = seeds
        self.listing = listing
        self.attrs = attrs
        self.available_json = available_json
        if header:
            self.header=header #if website needs a custom header
        else:
            self.header = get_http_headers()

    
    def scrape_one_item(self,url):
        """To scrape one item from a given url

        Args:
            url (str): url of the item

        Returns:
            dict: dict of the item
        """
        session = requests.Session() 
        #randomize user-agent in every request
        random_ua =  get_random_ua()
        header_template = self.header
        header_template['user-agent'] = random_ua
        session.headers.update(header_template)

        res = session.get('https://www.coolinarika.com/api/auth/session') #auth session first
        # print('auth results: ', res.text)
        # print('auth response code: ', res.status_code)

        # #ID_HARDCODE = '-b2f43eb2-9e58-11ec-9f58-3e4f582a8920'
        # ID_HARDCODE = ''

        time.sleep(2)
        #add home page url to the obtained item url if item url is not complete
        if self.main_page not in url:
            res = session.get(self.main_page + url)
        else:
            url = url 
            res = session.get(url)

        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        if res.status_code == 200:
            try:
                #print(res.status_code)
                doc = html.document_fromstring(res.text)
                #set default values for variables

                if self.available_json:
                    #load the json containing the data from the script
                    #script_data = json.loads(doc.xpath(self.available_json['xpath']))

                    script_data = demjson.decode(doc.xpath(self.available_json['xpath']))

                    #print(script_data) 

                    name = script_data.get(self.attrs['name'])
                
                    ingredients = []
                    ingredients = script_data.get(self.attrs['ingredients'])
                    #ingredients = ' '.join(ingredients)# join ingredients

                    instructions = []
                    inst_list_web= script_data.get(self.attrs['instructions'])
                
                    for instruction in inst_list_web:
                        instructions.append(instruction['text'])

                    servings = script_data.get(self.attrs['servings'])

                    category = script_data.get(self.attrs['category'])


                    total_time = script_data.get(self.attrs['total_time'])
                    #total_time = self.process_time(total_time)
                    prep_time = script_data.get(self.attrs['prep_time'])
                    cook_time = script_data.get(self.attrs['cook_time'])

                    return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
                'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
                    
                    
                
                else: #if there's no available script_json
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
                    else: ingredients = doc.xpath(self.attrs['ingredients'])

                    #instructions
                    if self.check_normalize_space(self.attrs['instructions']):
                        instructions = doc.xpath(self.attrs['instructions'])
                    else:  instructions = doc.xpath(self.attrs['instructions'])

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
                return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}

                #raise Exception(e)


        else:
            #raise Exception('Cannot open one menu url, status code = {}, url = {}'.format(res.status_code, url))
            print('Cannot open one recipe url, status code = {}, url = {}'.format(res.status_code, url))
            return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}

    

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
        res = session.get('https://www.coolinarika.com/api/auth/session') #auth session first
    
        res = session.get(page_url)
        url_base = 'https://www.coolinarika.com/recept/'
        if res.status_code == 200:
            #doc = html.document_fromstring(res.text)
            listing = demjson.decode(res.text)
            #print('got items from url: ', page_url)
            #print(listing)
            urls = []
           
            for recipe in listing:
                try:
                    if 'image' not in recipe:
                        pass
                    else:
                        urls.append(url_base + recipe.get('slug'))
                except:
                    print(recipe)
            return urls
        else:
            #raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))
            print('Cannot open the menu url, status code = {}, url= {}'.format(res.status_code, page_url))
            return []
    
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
        try:
            for seed_url in self.seeds:
                if self.listing['next']['type'] == 'url':
                    for i in range(max_pages):
                        listing_items = []
                        page_url = seed_url + self.listing['next']['next_page_str'].format(i+1)
                        print('spider is scraping page: {}'.format(i+1))
                        #print('spider is scraping url: ', page_url)
                        listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
                        if not listing_items:
                            break #last page
                        if multithread: 
                            #pool = Pool() #initialize Pathos multiprocessing pool
                            pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
                            results  = pool.map(self.scrape_one_item, [url for url in listing_items])
                            #print('scraping - multithreaded, n items: ', len(listing_items))
                            pool.close() #close the multiprocessing  pool
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
                # 
                if self.listing['next']['type'] == 'custom_modify_url':
                    for i in range(max_pages):
                        listing_items = []
                        page_url = seed_url.format(i+1)
                        #print('spider is scraping page: {}'.format(i+1))
                        #print('spider is scraping url: ', page_url)
                        listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
                        if not listing_items:
                            break #last page
                        if multithread: 
                            #pool = Pool() #initialize Pathos multiprocessing pool
                            pool = mp.Pool(mp.cpu_count()) #initialize multiprocessing pool
                            results  = pool.map(self.scrape_one_item, [url for url in listing_items])
                            #print('scraping - multithreaded, n items: ', len(listing_items))
                            pool.close() #close the multiprocessing  pool
                        else:
                            results = []
                            for item_url in listing_items:
                                item = self.scrape_one_item(item_url)
                                results.append(item)
                                                
                        all_items += results
        
            return all_items
            
        except Exception as e:
            print(e)
            return all_items