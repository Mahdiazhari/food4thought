
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
from  util.croatia.coolinarika import Coolinarika

def main():
    attrs = {
            'name':         'name',
            'ingredients':  'recipeIngredient',
            'total_time':   'totalTime',
            'instructions': 'recipeInstructions',
            'servings':     'recipeYield',
            'category':     'recipeCategory',
            'prep_time':    'prepTime',
            'cook_time':    'cookTime',
    }
    listing={'items': '', 'next': { 'next_page_str': '?page={}', 'type': 'url'}}
    seeds = ['https://api.coolinarika.com/api/v1/feed/recepti/novi']
    available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}


    #custom header
    custom_header_template = { #setup custom header because this website requires certain headers
            'referer': 'https://www.coolinarika.com/recept/brza-krompir-pita-b2f43eb2-9e58-11ec-9f58-3e4f582a8920',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-fetch-site' : 'same-origin',
            'cookie': '_gcl_au=1.1.2096643780.1648932938; _fbp=fb.1.1648932938479.532371783; _hjSessionUser_1123566=eyJpZCI6IjE4Y2YyOTdkLWI5ZGEtNTA0NC1iNTdkLTUxYTA4YTVmOTNlOSIsImNyZWF0ZWQiOjE2NDg5MzI5Mzg2NzgsImV4aXN0aW5nIjp0cnVlfQ==; abTestSrpRecomendations=N%2FA; coolinarika-pseudo-user-id=f96b2258-7a90-4b9e-b2f8-65647f041648; __Host-next-auth.csrf-token=eaa5b69dfdfb200837f597acb95978332cca599bda3de035dbf8770c8a165deb%7Caec6fa101367af9be6cf2773f37c110d6f39e0b6c44b7c0f949615e99d6734fc; __gfp_64b=WOjM6O0fdmBPy5tVlkR77ZCHtWY1l0l68dNF5lJgFtv.V7|1648932938; _gid=GA1.2.666841594.1649751255; __Secure-next-auth.callback-url=j%3A%22https%3A%2F%2Fwww.coolinarika.com%2F%22; _hjAbsoluteSessionInProgress=0; _hjSession_1123566=eyJpZCI6IjBjOWE2NWFlLWVhMzYtNDAxYi04MmM0LTBmYTk3YzlkZWExZSIsImNyZWF0ZWQiOjE2NDk3NTQ5OTM5ODEsImluU2FtcGxlIjpmYWxzZX0=; FCCDCF=[null,null,null,["CPWyprAPWyprAEsABBHRCJCgAAAAAH_AAA6IAAAOhQD2F2K2kKEkfjSeXYAQBCujoEIBUAAAAECDMAAAAUgQAgFIIAgAAlAAAAEAABAQEwCAgQQABAAAoACgACAAAAAAAAAAAAQQAABAAIAAAAQAAAEAQAAAAAQAAAAAAABAhAAAQQAEAAAAAAAAAAAAAAAAAAABAAA","1~","8650F57D-E772-4578-94DE-A833AEA1306B"],null,null,[]]; pageviewCount=5; _ga_TZHRD0NBQP=GS1.1.1649754913.4.1.1649756415.59; _ga=GA1.2.284449915.1648932939; _dc_gtm_UA-18370761-1=1',
            'user-agent': ''}


    croatia_spider = Coolinarika('https://www.coolinarika.com/recept', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json, header=custom_header_template)


    croatia_spider.scrape_one_item('https://www.coolinarika.com/recept/brza-krompir-pita')


    result_list = croatia_spider.start_scrape(max_pages=333)

    result_df = pd.DataFrame(result_list)
    result_df.to_csv('data/croatia/coratia_coolinarika.csv')

main()




