#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import re
import urlparse
import MySQLdb,socket

# 数据库操作类，记录已爬取的url和获取未爬取的url
class Database(object):

	def __init__(self):
		self.conn=MySQLdb.connect(
									host='127.0.0.1',
									user='root',
									passwd='12345678',
									db='spider'
									)
		self.cursor=self.conn.cursor()

	def write(self,url):
		if self.__has_url(url) is False:
			try:
				self.cursor.execute(r"insert into new_url (url) values ('%s')" % url)
				self.conn.commit()
			except Exception as e:
				print e
				self.conn.rollback()

	def __has_url(self,url):
		return self.cursor.execute(r"select url from old_url where url = '%s'" % url) != 0

	def readOne(self):
		if self.has_new_url():
			self.cursor.execute(r"select url from new_url limit 1")
			url = self.cursor.fetchone()[0]
			try:
				self.cursor.execute(r"delete from new_url where url = '%s'" % url)
				self.cursor.execute(r"insert into old_url (url) values ('%s')" % url)
				self.conn.commit()
			except Exception as e:
				print e
				self.conn.rollback()
			return url
		return None

	def has_new_url(self):
		return self.cursor.execute(r"select url from new_url") != 0

	def die(self):
		self.cursor.close()
		self.conn.close()



# 收集爬取到的数据以及将数据输出到文件中
class HtmlOutputer(object):

	def __init__(self):
		self.datas = []

	def collect(self,data):
		self.datas.append(data)

	def output(self):
		with open('output.html','wb') as f:
			f.write('<html>')
			f.write('<head><meta charset="UTF-8"></head>')
			f.write('<body>')
			f.write('<table>')
			try:
				for data in self.datas:
					f.write('<tr>')
					for content in data.itervalues():
						f.write('<td>')
						f.write(content.encode('utf-8'))
						f.write('</td>')
					f.write('</tr>')

					
			except Exception as e:
				print e
			finally:
				f.write('</table>')
				f.write('</body>')
				f.write('</html>')
				f.close()
			



# 解析网页数据
class HtmlParser(object):

	def parse(self,url,content):
		if url is None or content is None:
			return None

		soup = BeautifulSoup(content,'html.parser',from_encoding='utf-8')
		new_urls=self.__get_new_urls(url,soup)
		new_data=self.__get_new_data(url,soup)
		return new_urls,new_data

	def __get_new_urls(self,url,soup):
		new_urls=set()
		links = soup.find_all('a',href=re.compile('/view/\d+.htm'))
		for link in links:
			new_url=urlparse.urljoin(url,link['href'])
			new_urls.add(new_url)

		return new_urls

	def __get_new_data(self,url,soup):
		data={}
		data['url']=url
		# <dd class="lemmaWgt-lemmaTitle-title"> <h1>Python</h1>
		title = soup.find('dd',class_='lemmaWgt-lemmaTitle-title')
		if title !=None:
			title = title.find('h1')
		if title != None:
			data['title'] = title.get_text()
		else:
			data['title'] = ''

		# <div class="lemma-summary" label-module="lemmaSummary">
		summary = soup.find('div', class_='lemma-summary')
		if summary != None:
			data['summary'] = summary.get_text()
		else:
			data['summary'] = ''

		return data




# 下载网页内容
class HtmlDownloader(object):
	def download(self,url):
		if url is None:
			return None
		try:
			response = urllib2.urlopen(url)
		except urllib2.URLError:
			return None
		except urllib2.HTTPError:
			return None
		if response.getcode() != 200:
			return None
		return response.read()




# URL调度器
class UrlManager(object):
	def __init__(self):
		self.database=Database()

	def add_new_url(self,url):
		self.database.write(url)

	def add_new_urls(self,urls):
		if urls is None or len(urls) == 0:
			return
		for url in urls:
			self.add_new_url(url)

	def has_new_url(self):
		return self.database.has_new_url()

	def get_new_url(self):
		return self.database.readOne()

	def quit(self):
		self.database.die()



# 爬虫主程序
class SpiderMain(object):
	def __init__(self):
		self.url_manager=UrlManager()
		self.downloader=HtmlDownloader()
		self.parser=HtmlParser()
		self.outputer=HtmlOutputer()

	def craw(self, url):
		num=0
		self.url_manager.add_new_url(url)
		while self.url_manager.has_new_url() and num < 10:
			url = self.url_manager.get_new_url() 
			print url
			# 下载网页内容
			content=self.downloader.download(url)
			if content is None:
				print "Craw failed"
				continue
			#解析网页数据
			data = self.parser.parse(url, content)
			if data is None:
				print "Craw failed"
				continue
			new_urls = data[0]
			new_data = data[1]
			# 收集解析后爬取的数据
			self.url_manager.add_new_urls(new_urls)
			self.outputer.collect(new_data)

			num+=1

		self.outputer.output()




if __name__ == '__main__':
	root_url= "https://movie.douban.com/subject/26363254/" 
    #"http://baike.baidu.com/view/21087.htm"
	spider = SpiderMain()
	spider.craw(root_url)

