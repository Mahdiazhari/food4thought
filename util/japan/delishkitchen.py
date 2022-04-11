import pandas as pd
import json
import requests
from lxml import html
import re
from util.http_utility import get_http_headers
import multiprocessing as mp
#from pathos.multiprocessing import ProcessingPool as Pool #python package which enables multiprocessing on child classes
import time


class DelishKitchen: 
    #since we cannot use class instances for multiprocessing, we have to separate this into a class of its own.
   
    """This class extends the main Spider Class for Scraping Delish TV recipe website. We had to separate it to another class because
        multiprocessing does not work on child instances, and jupyter notebook is iffy with importing classes.

    Args:
        Spider (_type_): _description_
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

    #Process the duration format from the recipes website
    def process_time(self,time_str):
        try:
            if 'S' in time_str:
                #hours = time_str.split("H")[0]
                seconds  = time_str.split("PT")[1].split('S')[0]
                #minutes = re.findall(r'\b\d+\b', time_str.split("H")[1])
                # print(hours)
                # print(minutes)
                return seconds
            else:
                return time_str
        except:
            return time_str
    
    # def check_normalize_space(self,xpath):
    #     super().check_normalize_space(xpath)

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
            if self.listing['next']['type'] == 'url':
                for i in range(max_pages):
                    listing_items = []
                    page_url = seed_url + self.listing['next']['next_page_str'].format(i+1)
                    print('spider is scraping page: {}'.format(i+1))
                    #print('spider is scraping url: ', page_url)
                    listing_items = self.get_items_from_page(page_url)
                    if not listing_items:
                        break #last page
                    listing_items = list(set(listing_items)) #convert to set to remove duplicate urls
                    if multithread: 
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


    def scrape_one_item(self,url):
        """To scrape one item from a given url.

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
        
        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        if res.status_code == 200:
            try:
                #print(res.status_code)
                doc = html.document_fromstring(res.text)
                
                #get data from script application json with recipeIngredient
                script_data = json.loads(doc.xpath("normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"))
                #print(script_data)

                name = script_data.get('name')
                
                ingredients = []
                ingredients = script_data.get('recipeIngredient')
                #ingredients = ' '.join(ingredients)# join ingredients

                instructions = []
                inst_list_web= script_data.get('recipeInstructions')
            

                for instruction in inst_list_web:
                    instructions.append(instruction['text'])
               # instructions= ' '.join(instructions) #join all as one


                servings = script_data.get('recipeYield')

                category = doc.xpath('normalize-space(//ul[@class="categories"])')


                total_time = script_data.get('totalTime')
                total_time = self.process_time(total_time)
                
                #for this website the cooktime and preptime are misleading
        
                #cook_time = script_data.get('cookTime')
                #prep_time = script_data.get('prepTime')

                return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
                'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
            
            except Exception as e:
                print('something is wrong for item: {}'.format(url)) 
                pass

        else:
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
        session.headers.update(self.header)
        res = session.get(page_url)
        if res.status_code == 200:
            doc = html.document_fromstring(res.text)
            urls = doc.xpath(self.listing['items'])
            #print('got items from url: ', page_url)
            return urls
        else:
            print('Cannot open the menu url, status code = {}, url= {}'.format(res.status_code, page_url))
            return []
