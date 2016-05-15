# !usr/bin/env python3
# -- coding:utf-8 --

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import re
import os
import threading
import struct
import array
import json
import time
import traceback

class WorkingThread(threading.Thread):
    def __init__(self, socket, url, urlList, address, imgList):
        threading.Thread.__init__(self)
        self.socket = socket
        self.url = url
        self.urlList = urlList
        self.address = address
        self.position = address.__len__()

        self.finish = False

        self.imgList = imgList

    def run(self):
        adres = self.url[0:self.position]
        if adres != self.address:
            print('not this adress pass')
            self.finish = True
            return
        try:
            headers = [
                ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'),  
                # ('Connection', 'keep-alive'),  
                # ('Cache-Control', 'no-cache'),  
                # ('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'),  
                # ('Accept-Encoding', 'gzip, deflate, utf-8'),  
                ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            ]
            # proxy_support = urllib.request.ProxyHandler({'http':'115.218.220.100:9000'})
            # proxy_auth_handler = urllib.request.ProxyBasicAuthHandler();
            # opener = urllib.request.build_opener(proxy_support, proxy_auth_handler)
            # opener.addheaders = headers
            # urllib.request.install_opener(opener)
            # data = urllib.request.urlretrieve(self.url)

            # req = urllib.request.Request(self.url)
            # req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
            # data = urllib.request.urlopen(req);

            opener = urllib.request.build_opener()
            # opener.addheaders = headers

            time.sleep(2)

            data = opener.open(self.url);
            page = data.read().decode()

            self.urlList.extend(list(set(re.findall(r'<a.+?href="(http://www\.meitulu\.com/.+?)"', page))))

            self.imgList.extend(list(set(re.findall(r'<img.+?src="(http://pic\.yiipic\.com/.+?)"',page))))
            print('thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(self.imgList)
            print('thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        except Exception as e:
            print('thread>>>>>>>>>>>>>>>>>>>>>>>>>>>1')
            print(self.url)
            print('thread>>>>>>>>>>>>>>>>>>>>>>>>>>>2')
            print(self.imgList)
            print('thread>>>>>>>>>>>>>>>>>>>>>>>>>>>3')
            print(e)
            print('thread>>>>>>>>>>>>>>>>>>>>>>>>>>>4')
        finally:
            self.finish = True

    def isFinish(self):
        return self.finish

