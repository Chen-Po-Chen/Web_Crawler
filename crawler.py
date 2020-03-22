import urllib.request as req
import numpy as np
import datetime
import pymysql
import random
import time
import bs4
import sys
import os
sys.setrecursionlimit(5000000)

# PTT web info
PTT_URL_HEAD = "https://www.ptt.cc"
PTT_HOTBOARDS_URL = "/bbs/hotboards.html"
MAX_PAGE = 40000
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
COOKIE = "over18=1"

SERVER_INFO = ["localhost",			# IP
				"root",				# User Name
				"*****",			# Password
				"ptt_hot_article"]	# Database Name

def connect_data_base():
	db = pymysql.connect(SERVER_INFO[0], SERVER_INFO[1], SERVER_INFO[2], SERVER_INFO[3])
	return db

def close_data_base(db):
	db.close()

def upload_404_log(db):
	cursor = db.cursor()
	try:
		cursor.execute("INSERT INTO log VALUES(%s)", (str(datetime.datetime.now())))
	except:
		cursor.execute("CREATE TABLE log(log_information CHAR(100), time_information CHAR(30))")
		cursor.execute("INSERT INTO log VALUES(%s)", (str(datetime.datetime.now())))
	db.commit()

def upload_ulr_list(db, url):
	cursor = db.cursor()
	cursor.execute("INSERT INTO URL_list VALUES(%s)", url[0])
	db.commit()

def download_url_list(db):
	cursor = db.cursor()
	try:
		cursor.execute("SELECT * FROM URL_list")
		url = list(cursor.fetchall())
	except:
		cursor.execute("CREATE TABLE URL_list(web_url CHAR(100) NOT NULL)")
		url = []
	db.commit()
	return url, cursor

def upload_article_info(db, article_info):
	cursor = db.cursor()
	try:
		cursor.execute("INSERT INTO Article_Info VALUES(%s, %s, %s, %s, %s, %s)", article_info)
	except:
		cursor.execute("CREATE TABLE Article_Info(Author_ID CHAR(20), Author_Name CHAR(20), Article_Title CHAR(200), Published_Time CHAR(30), Contect VARCHAR(2000), Article_URL CHAR(100))")
		cursor.execute("INSERT INTO Article_Info VALUES(%s, %s, %s, %s, %s, %s)", article_info)
	db.commit()

def upload_comment_info(db, article_info, comment_info):
	cursor = db.cursor()
	article_info[0] = article_info[0].replace(":","")
	article_info[0] = article_info[0].replace(" ","")
	article_info[3] = article_info[3].replace(":","_")
	article_info[3] = article_info[3].replace(" ","_")
	file_name = "Comment_Info_" + article_info[0] + "_" + article_info[3]
	create =  "CREATE TABLE " + file_name +"(Tag CHAR(8) ,Author_ID CHAR(20) NOT NULL, Published_Time CHAR(30), Contect VARCHAR(500))"
	insert = "INSERT INTO " + file_name + " VALUES(%s, %s, %s, %s)"
	try:
		cursor.executemany(insert, comment_info)
	except:
		cursor.execute(create)
		cursor.executemany(insert, comment_info)
	db.commit()

def check_date_input(date_start, date_end):
	try:
		date_s = time.strptime(date_start+" 00:00:00", "%Y/%m/%d %H:%M:%S")
		date_e = time.strptime(date_end+" 23:59:59", "%Y/%m/%d %H:%M:%S")
		date_s = int(time.mktime(date_s))
		date_e = int(time.mktime(date_e))
		if date_e >= date_s:
			check = True
		else:
			check = False
			print("輸入錯誤: 起始日期比結束日期晚")
		return date_s, date_e, check
	except:
		date_s = 0
		date_e = 0
		check = False
		print("請確認輸入日期或格式(yyyy/mm/dd)")
	return date_s, date_e, check

def convert_date(date, p_date):
	if date[0] == " ":
		date = date.replace(" ", "0")
	# print(p_date[-4:]+"/"+date)
	date = time.strptime(p_date[-4:]+"/"+date+" 12:00:00", "%Y/%m/%d %H:%M:%S")
	date = int(time.mktime(date))
	return date

def open_web(web_url):
	time.sleep(random.randrange(3,5))
	print("Opening: "+web_url)
	request = req.Request(web_url, headers={"cookie":COOKIE,"User-Agent":USER_AGENT})
	try:
		with req.urlopen(request) as response:
			data = response.read().decode("utf-8")
		web_data = bs4.BeautifulSoup(data, "html.parser")
	except:
		web_data = False
	return web_data

def author_info(article_data):
	author = article_data[0]
	s = author.find("(")
	e = author.find(")")
	author_id = article_data[0][:s-1]
	author_name = article_data[0][s+1:e]
	return author_id, author_name

def article_info(article_data, url):
	article_title = article_data[1]
	published_time = article_data[2]
	return article_title, published_time, url

def article_contect(article_data, published_time):
	contect_start = article_data.text.find(published_time)+24
	contect_end = article_data.text.find("※ 發信站: 批踢踢實業坊(ptt.cc)")
	contect = article_data.text[contect_start:contect_end]
	return contect

def article_comment(article_data):
	comment_data = []
	tags = []
	comment_author_ids = []
	comment_times = []
	replies = []
	pushes = article_data.find_all("div", class_="push")
	for push in pushes:
		try:
			comment_times.append(push.find("span", class_ = "push-ipdatetime").string[-11:-1])
		except:
			comment_times.append(np.nan)

		try:
			tags.append(push.find("span", class_ = "push-tag").string)
		except:
			tags.append(np.nan)
        
		try:
			comment_author_ids.append(push.find("span", class_ = "f3 hl push-userid").string)
		except:
			comment_author_ids.append(np.nan)
	
		try:
			replies.append(push.find("span", class_ = "f3 push-content").string[2:])
		except:
			replies.append(np.nan)

	for index in range(len(comment_times)):
		comment_data.append([tags[index], comment_author_ids[index], replies[index], comment_times[index]])
	return comment_data

def get_hotboard_url():
	print("Collecting URL......")
	hot_boards_url = []
	root = open_web(PTT_URL_HEAD+PTT_HOTBOARDS_URL)
	if root != False:
		raw_datas = root.find_all("div", class_="b-ent") ##find_all
		for raw_data in raw_datas:
			url = raw_data.find("a").get("href")
			hotboard_name = raw_data.find("div", class_="board-name")
			hot_boards_url.append([hotboard_name.string, url])
		return hot_boards_url
	else:
		return False

def web_page_info(root):
	page_info = root.find("div", class_="btn-group btn-group-paging")
	try:
		if page_info.find('a', class_="btn wide disabled").string == "下頁 ›":
			next_page = page_info.find_all('a', class_="btn wide")[1].get("href")
			final_page = False
		else:
			next_page = " "
			final_page = True
	except:
		next_page = page_info.find_all('a', class_="btn wide")[1].get("href")
		final_page = False
	# print(next_page, final_page)
	return next_page, final_page

def get_hot_article(hot_boards_url, date_s, date_e):
	for index in range(len(hot_boards_url)):
		root = open_web(PTT_URL_HEAD+hot_boards_url[index][1])
		if root != False:
			final_page = False
			page = 1
			while not(final_page):
				raw_datas = root.find_all("div", class_="title")
				date_data = root.find_all("div", class_="date")
				i = 0
				for raw_data in raw_datas:
					if raw_data.a != None:
						url = PTT_URL_HEAD+raw_data.find("a").get("href")
						date = date_data[i].string
						i+=1
						data_base = connect_data_base()
						url_list, cursor = download_url_list(data_base)
						if url_list != [] and url not in url_list[:][0]:
							upload_ulr_list(data_base, url)
							close_data_base(data_base)
							article_name = raw_data.a.string
							get_hot_article_raw_data(url, date_s, date_e, date)
						elif url_list == []:
							upload_ulr_list(data_base, url)
							close_data_base(data_base)
							article_name = raw_data.a.string
							get_hot_article_raw_data(url, date_s, date_e, date)
							
				next_page, final_page = web_page_info(root)
				if final_page == False:
					root = open_web(PTT_URL_HEAD+next_page)
				print(hot_boards_url[index][0]+' Page '+str(page)+' Down')
				page += 1
			print(hot_boards_url[index][0]+" Fin")
		else:
			try:
				log_file = open(SAVE_DATA_ROOT+'log.txt','r+')
				log = log_file.read()
				new_file = open(SAVE_DATA_ROOT+'log.txt','w')
				new_file.write(str(datetime.datetime.now())+" PTT 404 "+hot_boards_url[index][1]+" "+hot_boards_url[index][0]+'\n'+log)
				log_file.close()
				new_file.close()
			except:
				log_file = open(SAVE_DATA_ROOT+'log.txt','w+')
				log_file.write(str(datetime.datetime.now())+" PTT 404 "+hot_boards_url[index][1]+" "+hot_boards_url[index][0]+'\n')
				log_file.close()

def get_hot_article_raw_data(url, date_s, date_e, date):
	temp = []
	comment_data = []
	article_data = open_web(url)
	print("Reading......")
	datas = article_data.find_all("div", class_="article-metaline")
	# print(article_data)
	for data in datas:
		temp.append(data.text[2:])
	if temp != []:
		article_title, published_time, article_url = article_info(temp, url)
		article_date = convert_date(date, published_time)
		if article_date>=date_s and article_date<=date_e:
			author_id, author_name = author_info(temp)
			contect = article_contect(article_data, published_time)
			comment_data = article_comment(article_data)
			print(comment_data)
			article_d = [author_id, author_name, article_title, published_time, contect, article_url]
			print("Saving article: "+author_id+" "+article_title)
			data_base = connect_data_base()
			upload_article_info(data_base, article_d)
			close_data_base(data_base)
			data_base = connect_data_base()
			upload_comment_info(data_base, article_d, comment_data)
			close_data_base(data_base)
			# save_npy_data([author_id, author_name, article_title, published_time, contect, article_url], SAVE_DATA_ROOT+author_id+"_"+published_time.replace(":","_"))
			# save_npy_data(comment_data, SAVE_DATA_ROOT+author_id+"_"+published_time.replace(":","_")+"_comment data")
			print("Down")

def save_npy_data(data, file_name):
	np.save(file_name, data)

def load_npy_data(file_name):
	return np.load(file_name)

def main():
	if not os.path.exists(SAVE_DATA_ROOT):
		os.makedirs(SAVE_DATA_ROOT)
	input_date = True
	while input_date:
		date_start = input("請輸入起始日期(yyyy/mm/dd): ")
		date_end = input("請輸入結束日期(yyyy/mm/dd): ")
		date_s, date_e, input_date = check_date_input(date_start, date_end)
		input_date = not(input_date)

	url = get_hotboard_url()
	if url != False:
		get_hot_article(url, date_s, date_e)
	else:
		data_base = connect_data_base()
		upload_404_log(data_base)
		close_data_base(data_base)

main()
