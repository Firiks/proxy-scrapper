"""
Wrapper function for rotating proxies, handles requests and returns response, if some proxy fails it will be replaced with a new one
"""

import os
import requests
import json

CURRENT_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(CURRENT_DIR, 'cache')
HTTP_PROXIES = []
SOCKS_PROXIES = []

# keep track of working ips for url
working_ip_cache = []

# keep track of not working ips for url
not_working_ip_cache = []

def is_in_cache( proxy, type, url, cache_list ):
    for item in cache_list:
        if proxy['ip'] == item[0]['ip'] and type == item[1] and url == item[2]:
            return True

    return False

def load_proxies(type):
    with open(os.path.join(CACHE_DIR, f'{type}_proxies.json'), 'r') as f:
        proxies = json.load(f)
        return proxies

def get_proxy( type, url, cache ):
    # check if we have a working proxy for this url
    if cache and working_ip_cache:
        for proxy in working_ip_cache:
            if proxy['type'] == type and proxy['url'] == url:
                return proxy

    global HTTP_PROXIES
    global SOCKS_PROXIES

    if not HTTP_PROXIES:
        HTTP_PROXIES = load_proxies('http')

    if not SOCKS_PROXIES:
        SOCKS_PROXIES = load_proxies('socks')

    # if we don't have a working proxy, load a new one
    if type == 'http' and HTTP_PROXIES:
        for proxy in HTTP_PROXIES:
            if is_in_cache( proxy, type, url, not_working_ip_cache ): # ignore not working proxies
                continue

            if not cache and is_in_cache( proxy, type, url, working_ip_cache ): # ignore cached proxies
                continue

            return proxy

    if type == 'socks' and SOCKS_PROXIES:
        for proxy in SOCKS_PROXIES:
            if is_in_cache( proxy, type, url, not_working_ip_cache ):
                continue

            if not cache and is_in_cache( proxy, type, url, working_ip_cache ):
                continue

            return proxy

    return None

def proxy_request(url, type, method, params, headers, retries=5, cache=True):
    while proxy := get_proxy(type, url, cache):
        for i in range(retries):
            try:
                proxies = {}

                if type == 'http':
                    # set up http proxy
                    for protocol in proxy['protocols']:
                        proxies[protocol] = f'{protocol}://{proxy["ip"]}'

                elif type == 'socks':
                    # set up socks proxy
                    for protocol in proxy['protocols']:
                        proxies['http'] = f'{protocol}://{proxy["ip"]}'
                        proxies['https'] = f'{protocol}://{proxy["ip"]}'

                response = requests.request(method, url, params=params, headers=headers, proxies=proxies, timeout=15)
                if response.ok:
                    if not is_in_cache( proxy, type, url, working_ip_cache ):
                        working_ip_cache.append( [ proxy , type, url ] )
                        return response

                # check if last retry
                if i == retries - 1:
                    if not is_in_cache( proxy, type, url, not_working_ip_cache ):
                        not_working_ip_cache.append( proxy )

            except Exception as e:
                print(f"Request failed with proxy {proxy['ip']}, retrying {i+1}/{retries}")

    return None

def main():
    # try to access a website with a proxy

    website = 'https://httpbin.org/ip'

    response = proxy_request(website, 'http', 'GET', None, None)

    print(response.text)

    # try socks proxy

    response = proxy_request(website, 'socks', 'GET', None, None)

    print(response.text)

if __name__ == '__main__':
    main()