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
import socket

from WorkingThread import WorkingThread

class UrlManager(threading.Thread):
	
	def __init__(self, socket, url, head, path, show):
		threading.Thread.__init__(self)

		self.path = path
		self.imgLists = []

		self.socket = socket
		self.url = url
		self.urlList = []
		self.historyList = []

		self.threadMaxSize = 4
		self.ThreadList = []

		self.tempLists = []
		self.head = head

		self.show = show;

		self.imgCount = 0;

	def run(self):
		try: 
			socket.setdefaulttimeout(30)
			headers = [
                ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'),  
                # ('Connection', 'keep-alive'),  
                # ('Cache-Control', 'no-cache'),  
                # ('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'),  
                # ('Accept-Encoding', 'gzip, deflate, utf-8'),  
                ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            ]
			# cj = http.cookiejar.LWPCookieJar()  
			# cookie_support = urllib.request.HTTPCookieProcessor(cj)  
			# opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)  
			# urllib.request.install_opener(opener) 

			# proxy_support = urllib.request.ProxyHandler({'http':'115.218.220.100:9000'})
			# proxy_auth_handler = urllib.request.ProxyBasicAuthHandler();
			# opener = urllib.request.build_opener(proxy_support, proxy_auth_handler)
			# print('00000000000000000')
			# proxy_support = urllib.request.ProxyHandler({'http':'115.218.220.100:9000'})
			# print('11111111111111111')
			# opener = urllib.request.build_opener(proxy_support)
			# opener.addheaders = headers
			# urllib.request.install_opener(opener)
			# print('2222222222222222222')
			# data = urllib.request.urlretrieve(self.url)
			# print('333333333333333333')

			# req = urllib.request.Request(self.url)
			# req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
			# data = urllib.request.urlopen(req);

			opener = urllib.request.build_opener()
			# opener.addheaders = headers
			# data = opener.open(self.url);
			print('------------->1')
			data = opener.open(self.url)
			page = data.read().decode()

			self.urlList.append('')
			self.urlList.extend(list(set(self.urlList+re.findall(r'<a.+?href="(http://www\.meitulu\.com/.+?)"', page))))
			print(self.urlList)

			if self.urlList.__len__() == 0:
				print('urlList has no url, return')
				return

			data_json = {}
			data_json['type'] = 'imgs'
			while self.urlList.__len__() != 0:

				time.sleep(1)
				
				while self.ThreadList.__len__() < self.threadMaxSize:
					tempUrl = self.urlList.pop(0)
					print(tempUrl)
					if self.urlList.__len__() == 0:
						print('finish urlList')
						return
					tempList = []
					imgList = []
					t = WorkingThread(self.socket, "{}{}".format(self.head, tempUrl), tempList, self.url, imgList)
					t.setDaemon(True)
					self.ThreadList.append(t)
					self.tempLists.append(tempList)
					self.imgLists.append(imgList)
					self.historyList.append(tempUrl)
					self.historyList = list(set(self.historyList))
					t.start()

				count = 0
				for t in self.ThreadList:
					if t.isFinish():
						print('a thread finish')
						l = list(set(self.tempLists[count]) - set(self.historyList))
						self.urlList.extend(l)
						self.urlList = list(set(self.urlList))

						for img in self.imgLists[count]:
							http = img[0:4];
							if http != 'http':
								img = self.url+img
							picName = self.path + os.sep + img.replace('/','_')
							try:
								urllib.request.urlretrieve(img, picName)
								print('download an image ---->' + str(self.imgCount))
								self.imgCount += 1
								if self.show:
									data = []
									data.append(img)
									data_json['args'] = data
									self.send_data(json.dumps(data_json))
							except:
								print('download image timeout')
								continue
						self.imgLists.remove(self.imgLists[count])
						self.ThreadList.remove(t)
						self.tempLists.remove(self.tempLists[count])
						print('remove a finish thrad')
					else:
						continue
					count += 1

				self.urlList = list(set(self.urlList) - set(self.historyList))
		except Exception as e:
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>1')
			print('urls size -->'+str(self.urlList.__len__()))
			print('threads count -->'+str(self.ThreadList.__len__()))
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>2')
			print(e)
			print('>>>>>>>>>>>>>>>>>>>>>>>>>>>3')
		finally:
			pass

	def unpack_frame(self, data):
		frame = {}
		byte1, byte2 = struct.unpack_from('!BB', data)
		frame['fin'] = (byte1 >> 7) & 1
		frame['opcode'] = byte1 & 0xf
		masked = (byte2 >> 7) & 1
		frame['masked'] = masked
		mask_offset = 4 if masked else 0
		payload_hint = byte2 & 0x7f
		if payload_hint < 126:
			payload_offset = 2
			payload_length = payload_hint
		elif payload_hint == 126:
			payload_offset = 4
			payload_length = struct.unpack_from('!H', data, 2)[0]
		elif payload_hint == 127:
			payload_offset = 8
			payload_length = struct.unpack_from('!Q', data, 2)[0]
		frame['length'] = payload_length
		payload = array.array('B')
		payload.fromstring(data[payload_offset + mask_offset:])
		if masked:
			mask_bytes = struct.unpack_from('!BBBB', data, payload_offset)
			for i in range(len(payload)):
				payload[i] ^= mask_bytes[i % 4]
		frame['payload'] = payload.tostring()

		return frame['payload'].decode('utf-8')

	def recv_data(self, num):
		frame = self.unpack_frame(num)
		if len(frame) < 1:
			return

		return frame['payload'].decode('utf-8')

	def send_data(self, data):
		if data:
			data = str(data)
		else:
			return False
		token = b'\x81'
		data = data.encode()
		length = len(data)
		if length < 126:
			token += struct.pack('B', length)
		elif length <= 0xFFFF:
			token += struct.pack('!BH', 126, length)
		else:
			token += struct.pack('!BQ', 127, length)
		data = token + data
		self.socket.send(data)
		return True

