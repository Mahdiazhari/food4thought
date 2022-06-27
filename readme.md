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



## Using the Spider Class (and it's child classes)

1. From the notebook (scrape-[Country Name]) file, import the package

```
from util.spider import Spider
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
        2. next: xpath governing the next page type of the website
        For this next there are various types developed to handle different recipe website cases:
            * 
            *
            *
        3. 








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
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}
seeds = ['https://www.myalbanianfood.com']
listing={'items': '//div[@class="masonry-grid"]//h2[@class="entry-title"]/a/@href', 'next': { 'next_page_str': '/page/{}', 'type': 'url'}}
```







