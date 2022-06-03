import json
import requests
from lxml import html
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua 
import multiprocessing as mp
#from pathos.multiprocessing import ProcessingPool as Pool #python package which enables multiprocessing on child classes
import time
import demjson
import random 
import undetected_chromedriver.v2 

from  util.spider import Spider

class ArmenianKitchen(Spider):
    """Class to scrape from ArmenianKitchen website

    Args:
        Spider (_type_): Inherits from the main spider class
    """
    
    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)

    def scrape_via_xpath(self, doc):
        """
        Function to scrape via xpath method

        Args:
            doc (_type_): takes the html document obtained from requests
        """
        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        if self.check_normalize_space(self.attrs['name']):
            name = doc.xpath(self.attrs['name'])
        else: name = doc.xpath(self.attrs['name'])[0]

        #Total Time
        try:
            if self.check_normalize_space(self.attrs['total_time']):
                total_time = doc.xpath(self.attrs['total_time'])
            else:  total_time = doc.xpath(self.attrs['total_time'])[0]
        except: pass

        #ingredients
        if isinstance(self.attrs['ingredients'], list):
            for xpath in self.attrs['ingredients']:
                ingredients = doc.xpath(xpath)
                if not ingredients:
                    pass
                else:
                    break
        else:
            ingredients = doc.xpath(self.attrs['ingredients'])

        #instructions
        if isinstance(self.attrs['instructions'], list):
            for xpath in self.attrs['instructions']:
                instructions = doc.xpath(xpath)
                if not instructions:
                    pass
                else:
                    break
        else:  
            instructions = doc.xpath(self.attrs['instructions'])

        #servings
        try:
            if isinstance(self.attrs['servings'], list):
                for xpath in self.attrs['servings']:
                    if self.check_normalize_space(xpath):
                        servings = doc.xpath(xpath)
                    else: 
                        servings = doc.xpath(xpath)[0]

                    if not servings:
                        pass
                    else:
                        break
            else:
                if self.check_normalize_space(self.attrs['servings']):
                    servings = doc.xpath(self.attrs['servings'])
                else: 
                    servings = doc.xpath(self.attrs['servings'])[0]
        except:
            #print('item has no serving data: {}'.format(url))
            servings = ''

        #category
        try:
            if isinstance(self.attrs['category'], list):
                for xpath in self.attrs['category']:
                    if self.check_normalize_space(xpath):
                        category = doc.xpath(xpath)
                    else: 
                        category = doc.xpath(xpath)[0]
                    
                    if not category:
                        pass
                    else:
                        break
            else:
                if self.check_normalize_space(self.attrs['category']):
                    category = doc.xpath(self.attrs['category'])
                else: 
                    category = doc.xpath(self.attrs['category'])[0]
        except:
            #print('item has no category data: {}'.format(url))
            category = ''

        #prep time
        try:
            if isinstance(self.attrs['prep_time'], list):
                for xpath in self.attrs['prep_time']:
                    if self.check_normalize_space(xpath):
                        prep_time = doc.xpath(xpath)
                    else: 
                        prep_time = doc.xpath(xpath)[0]
                    if not prep_time:
                        pass
                    else:
                        break
            else:
                if self.check_normalize_space(self.attrs['prep_time']):
                    prep_time = doc.xpath(self.attrs['prep_time'])
                else: 
                    prep_time = doc.xpath(self.attrs['prep_time'])[0]
        except:
            #print('item has no prep time data: {}'.format(url))
            prep_time = ''

        #cooking time
        try:
            if isinstance(self.attrs['cook_time'], list):
                for xpath in self.attrs['cook_time']:
                    
                    if self.check_normalize_space(xpath):
                        cook_time = doc.xpath(xpath)
                    else: 
                        cook_time = doc.xpath(xpath)[0]
                    if not cook_time:
                        pass
                    else:
                        break
            else:
                if self.check_normalize_space(self.attrs['cook_time']):
                    cook_time = doc.xpath(self.attrs['cook_time'])
                else: 
                    cook_time = doc.xpath(self.attrs['cook_time'])[0]
        except:
            #print('item has no cook time data: {}'.format(url))
            cook_time = ''

        #Returns the json of the item scraped (will return the empty template if nothing got scraped)
        return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
    'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}


    def scrape_one_item(self, url):
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
            res = session.get(self.main_page + url)
        else:
            res = session.get(url)

        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        if res.status_code == 200:
            try:

                #print('text doc: ', res.text)
                doc = html.document_fromstring(res.text)
                if self.available_json:
                    #load the json containing the data from the script
                    try:
                        script_data = json.loads(doc.xpath(self.available_json['xpath']))
                    except Exception as e:
                        print('json loads does not work')
                        print(e)
                        try:
                            script_data = demjson.decode(doc.xpath(self.available_json['xpath']))
                        except Exception as e :
                            print('cannot decode json with demjson')
                            print(e)
                            scraped_item = self.scrape_via_xpath(doc)
                            return scraped_item
                            

                    #print(isinstance(script_data,list)) 
                    if isinstance(script_data, list):
                        #print('its a list')
                        script_data = script_data[0]

                    if not script_data.get(self.attrs['name']):
                        if script_data.get('@graph'):
                            script_data = script_data.get('@graph')[-1] #get last element of graph list
                            script_type = str(script_data.get('@type'))
                            if 'recipe' not in script_type.lower():
                                print('please check the json schema again')
                        else: print('cant get data')
                   
                    json_attrs = {
                        'name':         'name',
                        'ingredients':  'recipeIngredient',
                        'total_time':   'totalTime',
                        'instructions': 'recipeInstructions',
                        'servings':     'recipeYield',
                        'category':     'recipeCategory',
                        'prep_time':    'prepTime',
                        'cook_time':    'cookTime',
                    }

                    name = script_data.get(json_attrs['name'])
                
                    ingredients = []
                    ingredients = script_data.get(json_attrs['ingredients'])
                    #ingredients = ' '.join(ingredients)# join ingredients

                    instructions = []
                    inst_list_web= script_data.get(json_attrs['instructions'])
                    
                    for instruction in inst_list_web:
                        if isinstance(instruction ,str):
                            instructions.append(instruction)
                            #print(instruction)
                        else:
                            #check if there is itemListElement inside
                            if instruction.get('itemListElement'):
                                item_list_element = instruction.get('itemListElement')
                                for item in item_list_element:
                                    instructions.append(item['text'])
                            else:
                                instructions.append(instruction['text'])

                    servings = script_data.get(json_attrs['servings'])

                    category = script_data.get(json_attrs['category'])


                    total_time = script_data.get(json_attrs['total_time'])
                    #total_time = self.process_time(total_time)
                    prep_time = script_data.get(json_attrs['prep_time'])
                    cook_time = script_data.get(json_attrs['cook_time'])

                    return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
                'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
                    
                    

            except Exception as e:
                print(e)
                print('something is wrong for item: {}'.format(url)) 
                #raise Exception(e)
                return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}

                

        else:
            #raise Exception('Cannot open one menu url, status code = {}, url = {}'.format(res.status_code, url))
            print('Cannot open one recipe url, status code = {}, url = {}'.format(res.status_code, url))
            return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}