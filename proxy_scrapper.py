# https://github.com/Shell1010/Proxy-scraper/blob/main/src/main.rs

import os
import re
import json
import requests
import queue
import threading
from logconfig import get_logger
from proxy_checker import ProxyChecker
from proxy_urls import http_urls, socks_urls

CURRENT_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(CURRENT_DIR, 'cache')
HTTP_FILE = os.path.join(CACHE_DIR, 'http_proxies.json')
SOCKS_FILE = os.path.join(CACHE_DIR, 'socks_proxies.json')
CHECKER = ProxyChecker()

logger = get_logger('proxy_scrapper')

def get_list_content(url):
    """Get all URLs from a text"""

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            logger.info(f"Got response from {url}")
            return response.text
    except:
        pass

    logger.error(f"Failed to get response from {url}")
    return None

def parse_ips(text):
    """Get all IPs from a text"""

    regex = r'\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b' # match ip address with optional port

    if text:
        return re.findall(regex, text)

    return []

def get_proxy_data(ip, protocols, q):
    """Get proxy data from an ip:port, add to queue if working"""

    global CHECKER

    proxy = CHECKER.check_proxy(ip, protocol=protocols)

    if proxy:
        logger.info(f"Working ip: {ip}")
        # add ip to proxy dict
        proxy['ip'] = ip

        # add proxy to queue
        q.put(proxy)
    else:
        logger.info(f"Invalid ip: {ip}")


def check_ips(ips, type):
    """Check if ip is working, add to queue if working"""

    all_results = []

    if ips and len(ips) > 0:
        threads = []
        results = queue.Queue()

        for ip in ips: # iterate through ips
            if type == 'http':
                t = threading.Thread(target=get_proxy_data, args=(ip, ['http', 'https'], results))
                t.start()
                threads.append(t)

            elif type == 'socks':
                t = threading.Thread(target=get_proxy_data, args=(ip, ['socks4', 'socks5'], results))
                t.start()
                threads.append(t)

        # join threads
        for t in threads:
            t.join()

        # get results from queue
        while not results.empty():
            result = results.get()
            all_results.append(result)

    return all_results

def scrape_and_check(url, type):
    """Scrape and check proxies from a url, return list of working proxies"""

    text = get_list_content(url) # get text from url
    ips = parse_ips(text) # get list of ips from text
    
    working_proxies = check_ips(ips, type) # check if ips are working
    
    return working_proxies

def main():
    """Scrape and check proxies from all urls use threading, return list of working http and socks proxies"""

    http_proxies = []
    socks_proxies = []

    # scrape and check http proxies
    for url in http_urls:
        http_proxies += scrape_and_check(url, 'http')

    # scrape and check socks proxies
    for url in socks_urls:
        socks_proxies += scrape_and_check(url, 'socks')

    global HTTP_FILE
    global SOCKS_FILE

    json.dump(http_proxies, open(HTTP_FILE, 'w'))
    json.dump(socks_proxies, open(SOCKS_FILE, 'w'))

    logger.info(f"Found {len(http_proxies)} http proxies")
    logger.info(f"Found {len(socks_proxies)} socks proxies")

    logger.info("Done")

    exit(0)

if __name__ == '__main__':
    main()