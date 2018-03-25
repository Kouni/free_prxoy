#!/usr/bin/env python
# -*- coding:UTF-8 -*-

'''
1.  Renew PROXY LIST if the data is older than five minutes.
    Then save to *proxy_list.json*.
2.  Rendom get IP Information from proxy_list.json, then test it.
3.  coming soon...
'''

from urllib.request import (urlopen,
                            Request,
                            build_opener,
                            ProxyHandler,
                            install_opener)
from bs4 import BeautifulSoup
import lxml
import json
import os
import time
import random


'''Get newest proxy list from free-proxy-list.net.
And parsing list data to JSON format file(proxy_list.json)
'''


# Get proxy list and save to json file.
def renew_proxy_info():
    req = Request("https://free-proxy-list.net/#list",
                  headers={'User-Agent': 'Mozilla/5.0'})
    try:
        n = urlopen(req, timeout=1)
    except Exception as e:
        print('##### URLOPEN ERROR #####')
    else:
        with n:
            try:
                with open('cache.html', 'wt') as f:
                    f.write(n.read().decode('UTF-8'))
            except Exception as e:
                print('##### CACHE I/O ERROR #####')
            else:
                pass
    finally:
        n.close()

    # Parsing proxy list from HTML to JSON file.
    with open("cache.html") as c:
        soup = BeautifulSoup(c, "lxml")
        table_body = soup.find('tbody')
        ips = []

    for html_tr in table_body.find_all('tr'):
        tds = html_tr.find_all('td')
        ips.append({'IP_Address_td': tds[0].string,
                    'Port_td': tds[1].string,
                    'Code_td': tds[2].string,
                    'Country_td': tds[3].string,
                    'Anonymity_td': tds[4].string,
                    'Google_td': tds[5].string,
                    'Https_td': tds[6].string,
                    'Last_Checked_td': tds[7].string})
    with open('proxy_list.json', 'wt')as f:
        f.write(json.dumps(ips))


def get_random_ip():
    global conn_info
    try:
        with open('proxy_list.json', 'rt') as f:
            conn_info = json.dumps(random.choice(json.load(f)))
    except Exception as e:
        print('proxy_list.json I/O error.')
    else:
        return(conn_info)


# Valid proxy
def check_proxy():
    global proxy_info
    connectinfo = json.loads(conn_info)
    proxy_info = (connectinfo['IP_Address_td']) + \
        ':' + (connectinfo['Port_td'])
    opener = build_opener(ProxyHandler({'http': proxy_info}))
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    install_opener(opener)
    try:
        with urlopen('http://ifconfig.co/ip', timeout=5) as n:
            result = (n.read().decode('UTF-8') + ':' +
                      connectinfo['Port_td']).replace('\n', '')
    except Exception as e:
        return('proxy_invalid')
    else:
        return(result)


if __name__ == '__main__':
    # get_random_ip()
    # connectinfo = json.loads(conn_info)
    # print(connectinfo['IP_Address_td'])

    if not os.path.exists('proxy_list.json') \
            or time.time() - os.stat("proxy_list.json").st_mtime > 300:
        renew_proxy_info()
    get_random_ip()
    final_resule = check_proxy()
    while (final_resule == 'proxy_invalid'):
        # print('Faile: ', final_resule + ' ==> ' + proxy_info)
        get_random_ip()
        final_resule = check_proxy()
    print(final_resule)
