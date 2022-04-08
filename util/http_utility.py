from util.user_agent import get_random_ua


def get_http_headers():
    """Sets the http header
    Returns:
        dict: containing the header
    """
    user_agent = get_random_ua()


    return {
        'Accept-Language': 'en-US,en;q=0.9,id;q=0.8,ms;q=0.7',
        'referer': 'https://www.google.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': user_agent}

