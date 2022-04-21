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


class BangladeshiKitchen(Spider):

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
        #randomize user-agent in every request
        random_ua =  get_random_ua()
        header_template = self.header
        header_template['user-agent'] = random_ua
        session.headers.update(header_template)
        
        time.sleep(2)
        #add home page url to the obtained item url if item url is not complete
        if self.main_page not in url:
            url = self.main_page + url
            res = session.get(url)
        else:
            res = session.get(url)

        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        if res.status_code == 200:
            try:
                #print('text doc: ', res.text)
                doc = html.document_fromstring(res.text)

                
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
                other_xpath = '//div[@id="recipe_content_pro"]//p//text()'

                if self.check_normalize_space(self.attrs['instructions']):
                    instructions = doc.xpath(self.attrs['instructions'])
                else:  instructions = doc.xpath(self.attrs['instructions'])

                if not instructions: #if instructions for the recipe are not available in the ol node
                    instructions = doc.xpath(other_xpath)

                #servings
                try:
                    if self.attrs['servings']:
                        if self.check_normalize_space(self.attrs['servings']):
                            servings = doc.xpath(self.attrs['servings'])
                        else: servings = doc.xpath(self.attrs['servings'])[0]
                except:
                    print('item has no serving data: {}'.format(url))
                    servings = ''

                #category
                try:
                    if self.attrs['category']:
                        if self.check_normalize_space(self.attrs['category']):
                            category = doc.xpath(self.attrs['category'])
                        else: category = doc.xpath(self.attrs['category'])[0]
                except:
                    print('item has no category data: {}'.format(url))
                    category = ''

                #prep time
                try:
                    if self.attrs['prep_time']:
                        if self.check_normalize_space(self.attrs['prep_time']):
                            prep_time = doc.xpath(self.attrs['prep_time'])
                        else: prep_time = doc.xpath(self.attrs['prep_time'])[0]
                except:
                    print('item has no prep time data: {}'.format(url))
                    prep_time = ''

                #cooking time
                try:
                    if self.attrs['cook_time']:
                        if self.check_normalize_space(self.attrs['cook_time']):
                            cook_time = doc.xpath(self.attrs['cook_time'])
                        else: cook_time = doc.xpath(self.attrs['cook_time'])[0]
                except:
                    print('item has no cook time data: {}'.format(url))
                    cook_time = ''
                

                #get prep cooking and servings
                prep_cook_servings_xpath = '//div[@id="time-more-pro"]//strong//text()'
                three_info = doc.xpath(prep_cook_servings_xpath)
                try:
                    prep_time = three_info[0]
                except:
                    print('this item: {}'.format(url))
                    print('item has no prep time data')
                    pass
                try:

                    cook_time = three_info[1]
                except:
                    print('has no cook time data')
                    pass
                try:
                    servings = three_info[2]
                except:
                    print('has no servings data')
                    pass

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
