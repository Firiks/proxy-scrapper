# Proxy scrapper and proxy rotator

## Description
Scrap ips of http and socks proxies from list of proxy urls and save working proxies to file. Then use proxies from file to rotate requests.

## Quick start
- install pycurl `pip install ./whl/pycurl-7.45.1-cp310-cp310-win_amd64.whl` if you are not using windows or python 3.10 then download another version from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycurl)
- install requirements `pip install -r requirements.txt`
- run proxy_scrap.py to scrap proxies and cache them to json
- use proxy_rotate.py to rotate requests with proxies from json file