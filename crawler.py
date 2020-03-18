import urllib.request as req
import numpy as np
import bs4


PTT_URL_HEAD = "https://www.ptt.cc"
PTT_HOTBOARDS_URL = "/bbs/hotboards.html"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
COOKIE = "over18=1"

def open_web(web_url):
	request = req.Request(web_url, headers={"cookie":COOKIE,"User-Agent":USER_AGENT})
	with req.urlopen(request) as response:
		data = response.read().decode("utf-8")
	web_data = bs4.BeautifulSoup(data, "html.parser")
	return web_data

def save_npy_data(data, file_name):
	np.save(file_name, data)

def load_npy_data(file_name):
	return np.load(file_name)


def get_hotboard_url():
	hot_boards_url = []
	root = open_web(PTT_URL_HEAD+PTT_HOTBOARDS_URL)
	raw_datas = root.find_all("div", class_="b-ent") ##find_all
	for raw_data in raw_datas:
		url = raw_data.find("a").get("href")
		hotboard_name = raw_data.find("div", class_="board-name")
		hot_boards_url.append([hotboard_name.string, url])
	return hot_boards_url

def get_hot_article(hot_boards_url):
	hot_article = []
	for index in range(len(hot_boards_url)):
		root = open_web(PTT_URL_HEAD+hot_boards_url[index][1])
		raw_datas = root.find_all("div", class_="title")	
		for raw_data in raw_datas:
			if raw_data.a != None:
				url = PTT_URL_HEAD+raw_data.find("a").get("href")
				article_name = raw_data.a.string
				hot_article_raw_data = get_hot_article_raw_data(url)
				hot_article.append(hot_article_raw_data)
	
def get_hot_article_raw_data(url)
	article_info = []
	contect = []
	comment_data = []
	tags = []
	comment_author_ids = []
	comment_times = []
	replies = []

	article_data = open_web(url)
	datas = article_data.find_all("div", class_="article-metaline")
	for data in datas:
		article_data.append(data.text[2:])

	s = article_data[0].find("(")
	e = article_data[0].find(")")
	author_id = article_data[0][:s-1]
	author_name = article_data[0][s+1:e]
	article_title = article_data[1]
	published_time = article_data[2]
	article_url = url


	pushes = web_data.find_all("div", class_="push")
	for push in pushes:
	try:
		times.append(push.find("span", class_ = "push-ipdatetime").string[-11:-1])
	except:
		times.append(np.nan)

	try:
		tags.append(push.find("span", class_ = "push-tag").string)
	except:
		tags.append(np.nan)
        
	try:
		author_ids.append(push.find("span", class_ = "f3 hl push-userid").string)
	except:
		author_ids.append(np.nan)
	
	try:
		replies.append(push.find("span", class_ = "f3 push-content").string[2:])
	except:
		replies.append(np.nan)

for index in range(len(times)):
	comment_data.append([tags[index], author_ids[index], replies[index], times[index]])


	return author_id, author_name, article_title, published_time, contect, article_url, comment_data

url = get_hotboard_url()
get_hot_article(url)