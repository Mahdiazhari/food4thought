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

from  util.spider import Spider


class Atyabtabkha(Spider):
    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)
    
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
                #print(res.status_code)
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
                            print('cannot decode json')
                            print(e)

                    #print(script_data) 
                    script_data = script_data['@graph'][4]

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

    def start_scrape(self, max_pages=100, multithread=True):
        """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
        Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

         Args:
            max_pages (int): maximum number of pages to scrape, default =100 

        Returns:
            list: list containing the url of items for all seeds for all pages
        """

        COLUMN_NAMES = ['name','ingredients', 'total_time','instructions', 'servings','category','prep_time','cook_time']
        POST_URL = 'https://www.atyabtabkha.com/wp-admin/admin-ajax.php'
        all_items = []
        #try:
        for seed_url in self.seeds: #for this recipe website, the seeds will contain the payloads
            
            #payload = """&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=حساء&term_slug=%d8%ad%d8%b3%d8%a7%d8%a1&ingredient_id=0&featured_id2=0&featured_id=182902&pageNumber=15&maxPages=37&action=more_post_ajax"""
            max_page = int(re.findall('(?<=&maxPages=)(.*)(?=&)', seed_url)[0])
            print('max page: ', max_page)
            for i in range(max_page):
                payload = seed_url.format(i+1)
                listing_items = []
                page_url = seed_url.format(i+1)
                print('spider is scraping page: {}'.format(i+1))
                #print('spider is scraping url: ', page_url)
                session = requests.Session() 
                #randomize user-agent in every POST request
                random_ua =  get_random_ua()
                header_template = post_request_header_template = { 
        #setup custom header for this specific website
        'referer': 'https://www.atyabtabkha.com/tag/%d8%ad%d8%b3%d8%a7%d8%a1',
        'origin': 'https://www.atyabtabkha.com',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html, */*; q=0.01',
        'content-length': '203',
        'x-requested-with': 'XMLHttpRequest',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': '_ga=GA1.2.2043413896.1649685106; _em_vt=dc9870a6-f72f-411b-b424-c3d29eb09e75-18018e50ebd-44b0731e; _em_gc=FR; _em_mb=0; __gads=ID=5519c60738627206:T=1649685105:S=ALNI_MbEIBgkPyWRDLgqIaTGZxvaZFUWQQ; _em_dmp=1649685106605; _fbp=fb.1.1649685116695.793756757; _gid=GA1.2.1358426319.1649846104; _em_c3=1; _em_vi=7660eeab-beca-469b-97c7-f3eb87ddcea5-18027cbaa78-559a972a; _em_scf=[]; _em_lt=1649935200292; _em_ft=1649935124863; _em_pc=3; _gat_UA-11819255-18=1',
        'user-agent': ''
}
                header_template['user-agent'] = random_ua
                session.headers.update(header_template)
                res = session.post(POST_URL, data=payload, headers=header_template)
                if res.status_code == 200:
                    try:
                        doc = html.document_fromstring(res.text)
                        #extract item urls from listing page
                        items_xpath = '//div[contains(@class,"article--alt")]/a/@href'
                        urls = doc.xpath(items_xpath)
                        #print(urls)
                        print('amount of urls we got: ', len(urls))
                        listing_items = urls
                    except:
                        print('doc is probably empty')
                else:
                    print('failed')
                    print(res.status_code)
                listing_items = list(set(listing_items)) #convert to set to remove duplicate urls
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
    
