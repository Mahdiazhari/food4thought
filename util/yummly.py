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

from  util.spider import Spider

class Yummly(Spider):

    def __init__(self, main_page, seeds, listing, attrs, available_json, header=None ):
        super().__init__(main_page,seeds,listing,attrs, available_json, header)


    def start_scrape(self, max_pages=100, multithread=True):
        """Get all recipe items from the seeds given. Can choose to enable multiprocessing.
        Multiprocessing is used to immediately scrape all menu items from a list of menu urls, but be careful of blockers.

         Args:
            max_pages (int): maximum number of pages to scrape, default =100 

        Returns:
            list: list containing the url of items for all seeds for all pages
        """

        sample_seed = """  https://mapi.yummly.com/mapi/v19/content/search?solr.seo_boost=new&search=bahamian&q=bahamian&related-searches-as-cards=true&fullReviews=true&reviewsPerRecipe=4&add-indexable=10&start={start_index}&maxResult={max_num}&fetchUserCollections=false&allowedContent=single_recipe&allowedContent=suggested_search&allowedContent=related_search&allowedContent=article&allowedContent=video&allowedContent=generic_cta&guided-search=true&solr.view_type=search_seo
"""

        all_items = []
        #try:
        for page_url in self.seeds:
            item_urls = []
            session = requests.Session() 
            #randomize user-agent in every request
            random_ua =  get_random_ua()
            header_template = get_http_headers()
            header_template['user-agent'] = random_ua
            session.headers.update(header_template)
            #for i in range(0, max_page, 200):
            #page_url.format(start_index= 0, max_num = 1000)
            res = session.get(page_url)
            if res.status_code == 200:
                page_data = json.loads(res.text)
                urls = page_data.get('feed')

                print('length of feeds: ', len(urls))
                listing_items = [recipe.get('tracking-id') for recipe in urls]
                
                if multithread: # does not work for undetected chromedriver
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


            else:
                print('Cannot open the menu url, status code = {}, url= {}'.format(res.status_code, page_url))
                raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))


        return all_items

        # except Exception as e:
        #     print(e)
        #     return all_items
    
    def scrape_one_item(self, url):
        """ Scrape one item from Yummly using undetected chromedriver to bypass cloudflare restrictions.

        Args:
            url (_type_): url of the website to scrape

        Returns:
            _type_: json containing the recipe information
        """

        #add undetected chromedriver options
        options = uc.ChromeOptions()
        options.headless=True
        options.add_argument('--headless')
        driver = uc.Chrome(options=options)
        if self.main_page not in url: 
           url = self.main_page + url
           #print(url)
        driver.get(url)
        doc = html.document_fromstring(driver.page_source)
        name, total_time, ingredients, instructions, servings, category, prep_time, cook_time = '','','','','','','',''
        driver.close() #close chromedriver
        try:
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
                if not script_data.get(self.attrs['name']):
                    if script_data.get('@graph'):
                        script_data = script_data.get('@graph')[-1] #get last element of graph list
                    else: print('cant get data')
                    
                name = script_data.get(self.attrs['name'])
            
                ingredients = []
                ingredients = script_data.get(self.attrs['ingredients'])
                #ingredients = ' '.join(ingredients)# join ingredients

                try:
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
                except: pass

                servings = script_data.get(self.attrs['servings'])

                category = script_data.get(self.attrs['category'])


                total_time = script_data.get(self.attrs['total_time'])
                #total_time = self.process_time(total_time)
                prep_time = script_data.get(self.attrs['prep_time'])
                cook_time = script_data.get(self.attrs['cook_time'])

                return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
            'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}


        except Exception as e:
            print(e)
            print('something is wrong for item: {}'.format(url)) 
            return {'name': name, 'total_time': total_time, 'ingredients': ingredients, 'instructions': instructions, 'servings': servings,
        'category': category, 'prep_time': prep_time, 'cook_time': cook_time,}

            #raise Exception(e)


    




# if __name__ == "__main__":   

#     # chrome_options = Options()
#     # #chrome_options.add_argument("--disable-extensions")
#     # #chrome_options.add_argument("--disable-gpu")
#     # #chrome_options.add_argument("--no-sandbox") # linux only
#     # chrome_options.add_argument("--headless")

#     session = requests.Session() 
#     #randomize user-agent in every request
#     page_url = """  https://mapi.yummly.com/mapi/v19/content/search?solr.seo_boost=new&search=bahamian&q=bahamian&related-searches-as-cards=true&fullReviews=true&reviewsPerRecipe=4&add-indexable=10&start=300&maxResult=568&fetchUserCollections=false&allowedContent=single_recipe&allowedContent=suggested_search&allowedContent=related_search&allowedContent=article&allowedContent=video&allowedContent=generic_cta&guided-search=true&solr.view_type=search_seo
# """
#     random_ua =  get_random_ua()
#     header_template = get_http_headers()
#     header_template['user-agent'] = random_ua
#     session.headers.update(header_template)
#     res = session.get(page_url)
#     if res.status_code == 200:

#         page_data = json.loads(res.text)
#         urls = page_data.get('feed')
#         #doc = html.document_fromstring(res.text)
#         #urls = 
#         #print('got items from url: ', page_url)
#         print('length of feds: ', len(urls))
#     else:
#         #raise Exception('Cannot open the menu url, status code = {}'.format(res.status_code))
#         print('Cannot open the menu url, status code = {}, url= {}'.format(res.status_code, page_url))

    # options = uc.ChromeOptions()
    # options.headless=True
    # options.add_argument('--headless')
    # driver = uc.Chrome(options=options)

    # driver.get('https://www.yummly.com/recipe/Bahamian-Johnnycake-1189449')

    # doc = html.document_fromstring(driver.page_source)
    # recipe_schema_xpath = "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"

    # print(doc.xpath(recipe_schema_xpath))



