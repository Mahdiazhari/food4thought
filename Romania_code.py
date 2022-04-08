
import json
import requests
import random
from lxml import html
import re

from  util.spider import Spider
from parsel import Selector
from util.http_utility import get_http_headers
from util.user_agent import get_random_ua


def main(): 

    attrs = {
        'name': '//meta[@property="og:title"]/@content',
        'ingredients': '//meta[@itemprop="recipeIngredient"]/@content',
        'total_time': '//meta[@itemprop="totalTime"]/@content',
    }

    listing={}
    seeds = {}
   

    user_agent = get_random_ua()
    custom_header = {
        'referer': 'https://www.google.com/',
        'Accept-Language': '*',
        'Accept-Encoding': '*',
        'Accept': '*',
        'user-agent': user_agent}
    romania_spider = Spider(seeds= seeds, listing =listing,attrs= attrs, header=custom_header)
    print(romania_spider.attrs)
    romania_spider.scrape_one_item('https://www.bucataras.ro/retete/tort-pajistea-cu-flori-5-ani-de-bucataras-96417.html')


main()