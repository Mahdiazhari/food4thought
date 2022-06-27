# Scraping Project for DIME Analytics

This repository contains files and codes of the Object Oriented Webscraper I developed during my internship for DIME Analytics.

## How to Setup

### Recommended: Setup Python Virtual Environment
https://pythonbasics.org/virtualenv/
1. Create python environment 
2. Activate Python Enviroment: bin/activate
3. Install python packages from requirements.txt: pip install -r requirements.txt 

### Directly Install packages (Not Recommended)
1. pip install -r requirements.txt



## How to Start scraping with the Spider Class (and its child classes)

1. Import Packages and setup directories

From the notebook (scrape-[Country Name]) file, import the package

```
from util.spider import Spider
```

Modify the notebook's output directory as needed
for example:
```
OUTPUT = '\home\food4thought\data\raw'
```



2. Setup the parameters for the Spider class:
These parameters must be configured based on the recipe website

    1. attrs: contains xpaths for the recipe to scrape from. If the website can be scraped using the ld+json/script via Recipe Schema,
    https://schema.org/Recipe we can simply use:

    ```
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
    ```

    Otherwise, we have to code the xpath for the required attributes manually, for example for afghanistan:

    ```
    attrs = {
        'name':         'normalize-space(//h2[@itemprop="name"])',
        'ingredients':  '//li[@class="ingredient"]//text()',
        'total_time':   '//li[@class="ready-in"]/span[@class="value"]//text()',
        'instructions': '//p[@class="instructions"]//text()',
        'servings':     '//li[@class="servings"]/span[@class="value"]//text() | //li[@class="yield"]/span[@class="value"]//text() ',
        'category':     '',
        'prep_time':    '//li[@class="prep-time"]/span[@class="value"]//text()',
        'cook_time':    '//li[@class="cook-time"]/span[@class="value"]//text()',
    }
    ```

    2. available_json: if the website has any json/ld+ script from where we can extract information using the recipe Schema. Leave empty
    if the website does not have this.
    Example, find recipe json if there exists recipeIngredient variable:

    ```
    available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}
    ```


    3. seeds: urls of the many categories of recicpes from the website.
    For example, Zimbokitchen (Zimbabwe):


    ```
    seeds = ['https://www.zimbokitchen.com/category/meats/', 'https://www.zimbokitchen.com/category/vegetables/',]

    ```


    4. listing: How each of the items in the seeds are listed. Listing has 2 parameters:
        1. items: xpath of the recipe/item
        2. next: dictionary governing the next page type of the website and the xpath of the next page (if available).
        For example: here is a next page url. In this case the page number is put `{}` so that the program will fill it in iteratively.


        ```
         { 'next_page_str': '&page={}'
        ```

        For this next there are various types developed to handle different recipe website types:
            1. random_pages: Developed primarily to tackle russianfood.com since the website blocks scrapers after a few hundred scrapes. In this part, the spider class will randomly select pages from the website until it scrapes the max_items.
            If random_pages are used, the variables are:
            max_items: number of items to scrape
            items_per_page: number of items per page of the website
            max_pages: max number of pages available in the website
            Sample:


            ```
            { 'next_page_str': '&page={}', 'type': 'random_pages', 'max_items': 300, 'items_per_page': 50, 'max_pages': 20}
            ```


            1. url: the most common recipe website type. In this type, Spider will go through each page iteratively until the max_page (if specified in the spider).


            2. custom_modify_url: UNUSED. Initially developed to scrape justfood.tv. But was unused since the website has tough security (datadome).

            3. one_page: MOSTLY UNUSED if the website does not have any other pages. Case: Ireland website Delish.com

    5. Headers: OPTIONAL PARAMETER
    add this parameter for the Spider in case website requires extra cookies, or encoding 

    ```
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
    ```

    6. main_page:
        Because the website listing usually does not put the main homepage/url of the website in the recipe url obtained from the xpath, the Spider will check for this when it scrapes one recipe if given the homepage url as the first parameter.

        Example:

        ```
        https://delishkitchen.tv/recipes/225609951383388637
        ```
        We need to put:

        ```
        https://delishkitchen.tv
        ```
        As the first parameter (main_page parameter) of the Spider class.

        ```
        delishtv_spider= Spider('https://delishkitchen.tv', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json)
        ```


3. Testing Scraping after instantiating the Spider Class.

The spider class has three main functions:
    1. start_scrape: starts the scraping process, takes two parameters:
        1. max_pages: number of maximum pages on the website
        2. multithread: if scraping can be sped up using parallell processes
    2. scrape_one_item: scrapes one item and returns a dictionary, takes the recipe url as the parameter
    3. get_items_from_page: extracts to a list the list of urls of a recipe page.

To test if the spider works on one menu:

```
croatia_spider.scrape_one_item('https://www.coolinarika.com/recept/brza-krompir-pita')
```

sample output:

```
{'name': 'Brza krompir pita',
 'total_time': None,
 'ingredients': ['3 jaja',
  '1 casa ulja (100 ml)',
  '1 casa jogurta (120 ml)',
  '1 luk',
  '100 g feta sira',
  'persun',
  '1 mljevena crvena paprika',
  '2 case brasna (200 g)',
  '3 krompira (350 g)',
  '1/2 Prašak za pecivo Docela',
  'so, biber, vegeta',
  'sesam za preko'],
 'instructions': ['Jaja, jogurt i ulje sjediniti pa kasikom fino izmjesati, dodati izdrobljeni sir, papriku, persun po ukusu, sitno sjeckani luk, krompir na kocke ili po zelji sjecen, brasno pomjesano sa svim suhim sastojcima. Zaciniti po ukusu i dobro izmjesati.',
  'Usuti smjesu u pouljeni pleh i peci u zagrijanoj pecnici na 190 stepeni 25-30 minuta dok fino ne porumeni i krompir ne bude kuhan. Sluziti uz salatu po zelji i jogurt.'],
 'servings': None,
 'category': None,
 'prep_time': None,
 'cook_time': None}
```

4. Start Scraping

Use the star_scrape function to start scraping, however make sure to set the max_pages and multithread as required

```
result_list = croatia_spider.start_scrape(max_pages=333)
```


5. Convert the resulting list of items into a dataframe

```
result_df = pd.DataFrame(result_list)
```


6. Save Dataframe to CSV

OUTPUT is the directory to save the file
```
result_df.to_csv(OUTPUT + 'japan_delishkitchen.csv')
```



