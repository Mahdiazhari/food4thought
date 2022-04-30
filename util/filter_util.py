




def exclude_recipe(categories, exclusions= []):
    """This function creates a filter function to exclude certain recipes using pandas and lambda functions.

    Args:
        categories (_type_): This is the category variable in the pandas dataframe.
        exclusions (_type_, optional): List of strings of menu item categories to exclude. Defaults to default_exclusions.

    Returns:
        _type_: Boolean indicating if the item is to be excluded.
    """
    #list of default categories to exclude
    default_exclusions =  ['desserts', 'beverages', 'cocktails', 'drinks', 'drink', 'dessert']
    if not exclusions:
        exclusions = default_exclusions
    if categories:
        if isinstance(categories, list):
            for item in categories:
                if isinstance(item, str):
                    if item.lower() in exclusions: 
                        return True
            return False
        elif isinstance(categories, str):
            for cat in exclusions:
                if cat in categories.lower(): 
                    return True
            return False
        else:
            return False
    else: 
        return False



