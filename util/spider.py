import json
import requests
from lxml import html
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua 
import multiprocessing as mp
import time
import demjson
import random 
import undetected_chromedriver.v2 as uc #add undetected chromedriver v2 to scrape complicated websites with cloudflare
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class Spider:
    """Scraper Spider class for scraping recipes from countries. 

    Args:
        main_page (str): string containing the main url/homepage of the website
        seeds (list): list containing url of seed(s) (url categories of recipes, if separated)
        listing (dict): dictionary containing next and item list xpaths 
        attrs (dict): dictionary containing xpaths of the attributes to scrape
        headers (dict): dictionary of custom header template if the website needs predefined custom headers 
    """
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

    def check_normalize_space(self,xpath):
        """This function checks if there is normalize-space in the xpath. It will return True if that's the case

        Args:
            xpath (str): xpath to check

        Returns:
            Boolean: indicating presence of 'normalize-space'
        """
        if 'normalize-space' in xpath:
            return True
        else: return False


    def scrape_one_item(self,url):
        """To scrape one item from a given url.

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
        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''

        #add home page url to the obtained item url if item url is not complete
        try:
            if self.main_page not in url:
                res = session.get(self.main_page + url)
            else:
                res = session.get(url)
        except:
            return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}
    
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
                            try:
                                """ 
                                Attempt to obtain doc of html from using selenium webdriver.
                                """

                                print('cannot decode json with demjson')
                                print('trying selenium')
                                #print(e)
                                
                                #try with selenium
                                options = uc.ChromeOptions()
                                options.headless=True
                                options.add_argument('--headless')
                                driver = uc.Chrome(options=options)
                                driver.get(url)
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')]")))
                                doc = html.document_fromstring(driver.page_source)
                                script_data = json.loads(doc.xpath(self.available_json['xpath']))
                                driver.close()
                            except:
                                return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
                'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}

                
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
                   
                        
                    name = script_data.get(self.attrs['name'])
                
                    ingredients = []
                    ingredients = script_data.get(self.attrs['ingredients'])
                    #ingredients = ' '.join(ingredients)# join ingredients

                    instructions = []
                    inst_list_web= script_data.get(self.attrs['instructions'])
                    
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
        """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
        Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

         Args:
            max_pages (int): maximum number of pages to scrape, default =100 

        Returns:
            list: list containing the url of items for all seeds for all pages
        """

        #COLUMN_NAMES = ['name','ingredients', 'total_time','instructions', 'servings','category','prep_time','cook_time']

        all_items = []
        #try:
        for seed_url in self.seeds:
            if self.listing['next']['type'] == 'random_pages':
                max_items  = self.listing['next']['max_items'] 
                item_per_page = self.listing['next']['items_per_page']
                max_pages = self.listing['next']['max_pages']
                n_pages = int(max_items/item_per_page)
                random_pages = random.sample(range(1, max_pages), n_pages)
                for i in random_pages:
                    listing_items = []
                    page_url = seed_url + self.listing['next']['next_page_str'].format(i)
                    print('spider is scraping page: {}'.format(i+1))
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

            if self.listing['next']['type'] == 'url':
                for i in range(max_pages):
                    listing_items = []
                    page_url = seed_url + self.listing['next']['next_page_str'].format(i+1)
                    print('spider is scraping page: {}'.format(i+1))
                    #print('spider is scraping url: ', page_url)
                    listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
                    if not listing_items:
                        print('no items found for page: {}'.format(page_url))
                        break #last page probably
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

                    # for item_url in listing_items:
                    #     item = self.scrape_one_item(item_url)

                        #item_df = pd.DataFrame([item], columns=item.keys())
                        #df = pd.concat([df,item_df], ignore_index=True)
               # 
            if self.listing['next']['type'] == 'custom_modify_url':
                for i in range(max_pages):
                    listing_items = []
                    page_url = seed_url.format(i+1)
                    print('spider is scraping page: {}'.format(i+1))
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
            
            if self.listing['next']['type'] == 'one_page':
                page_url = seed_url
                listing_items = []
                listing_items = list(set(self.get_items_from_page(page_url))) #convert to set to remove duplicate urls
                if not listing_items:
                    print('no items found in seed:{}'.format(seed_url))
                results = []
                for item_url in listing_items:
                    item = self.scrape_one_item(item_url)
                    results.append(item)
                all_items += results

       
        return all_items

        # except Exception as e:
        #     print(e)
        #     return all_items
    
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
        time.sleep(2)
        if res.status_code == 200:
            doc = html.document_fromstring(res.text)
            urls = doc.xpath(self.listing['items'])
            #print('got items from url: ', page_url)
            if not urls:
                for r in range(5): #5 times retry
                    print('retrying... attempt {}'.format(r))
                    res2 = session.get(page_url)
                    if res2.status_code == 200:
                        doc2 = html.document_fromstring(res2.text)
                        urls = doc2.xpath(self.listing['items'])
                        if urls: 
                            break
            return urls
        else:
            #raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))
            print('Cannot open the menu url, status code = {}, url= {}'.format(res.status_code, page_url))
            return []




