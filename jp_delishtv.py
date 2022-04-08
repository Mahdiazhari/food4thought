# %%
import pandas as pd
import json
import requests
import random
from lxml import html
import re
import time

from  util.spider import Spider
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua

# %% [markdown]
# # Scrape Japan - Delishtv
# 
# 

# %% [markdown]
# https://delishkitchen.tv/

# %%
class DelishKitchen(Spider): #inherit Spider Class
    """This class extends the main Spider Class for Scraping Delish TV recipe website.

    Args:
        Spider (_type_): _description_
    """

    def __init__(self, main_page, seeds, listing, attrs, header=None):
        super().__init__(main_page,seeds,listing,attrs, header)

    #Process the duration format from the recipes website
    def process_time(self,time_str):
        if 'S' in time_str:
            #hours = time_str.split("H")[0]
            seconds  = time_str.split("PT")[1].split('S')[0]
            #minutes = re.findall(r'\b\d+\b', time_str.split("H")[1])
            # print(hours)
            # print(minutes)
            return seconds
        else:
            return time_str
    
    # def check_normalize_space(self,xpath):
    #     super().check_normalize_space(xpath)

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

        if res.status_code == 200:
            try:
                #print(res.status_code)
                doc = html.document_fromstring(res.text)
                #set default values for variables
                name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

                doc = html.document_fromstring(res.text)
                
                #get data from script application json with recipeIngredient
                script_data = json.loads(doc.xpath("normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"))
                #print(script_data)

                name = script_data.get('name')

                ingredients = script_data.get('recipeIngredient')
                ingredients = ' '.join(ingredients)# join ingredients

                instructions = []
                inst_list_web = script_data.get('recipeInstructions')

                for instruction in inst_list_web:
                    instructions.append(instruction['text'])
                instructions= ' '.join(instructions) #join all as one


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
                raise Exception('something is wrong for item: {}'.format(url)) from e


        else:
            raise Exception('Cannot open one menu url, status code = {}'.format(res.status_code))
    

    # def start_scrape(self, max_pages=100, multithread=True):
    #     super().start_scrape(max_pages,multithread)
    
    # def get_items_from_page(self, page_url):
    #     super().get_items_from_page(page_url)


# %%
listing={'items': '//ul[@class="columns with-max-three"]//div[contains(@class,"delish-renewal-recipe-item-card")]//a/@href', 'next': { 'next_page_str': '?page={}', 'type': 'url'}}
seeds = ['https://delishkitchen.tv/categories/19878']

#, 'https://delishkitchen.tv/categories/655', 'https://delishkitchen.tv/categories/17359', ]


# %%
delishtv_spider= DelishKitchen('https://delishkitchen.tv', seeds= seeds, listing =listing,attrs= '')

# %%
delishtv_spider.scrape_one_item('https://delishkitchen.tv/recipes/216142397518644383')

# %%
result_list = delishtv_spider.start_scrape(max_pages=1) #max page is only 130

# %%
result_list

# %%
print(result_list)

# %%



