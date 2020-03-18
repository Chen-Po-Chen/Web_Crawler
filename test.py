import urllib.request as req
import numpy as np
import bs4

PTT_URL_HEAD = "https://www.ptt.cc"
PTT_HOTBOARDS_URL = "/bbs/hotboards.html"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"

request = req.Request("https://www.ptt.cc/bbs/Gossiping/M.1584513520.A.F58.html", headers={"cookie":"over18=1","User-Agent":USER_AGENT})
with req.urlopen(request) as response:
	data = response.read().decode("utf-8")
web_data = bs4.BeautifulSoup(data, "html.parser")

#author = web_data.find("div", class_="article-metaline").find("span", class_="article-meta-value").string
datas = web_data.find_all("div", class_="article-metaline")
#published_time = web_data.find("div", class_="article-metaline").find("span", class_="article-meta-value").string
#url = raw_data.find("a").get("href")
artical_data = []
for data in datas:
	artical_data.append(data.text[2:])
	#start = data.find("<span class=\"article-meta-value\">")
	#print(type(data))
	#print(end)

author = artical_data[0]
artical_title = artical_data[1]
published_time = artical_data[2]
comment_data = []
s = author.find("(")
e = author.find(")")

author_id = author[:s-1]
author_name = author[s+1:e]

content = web_data.find(id="main-content").text

target_content = u'※ 發信站: 批踢踢實業坊(ptt.cc),'

content = content.split(target_content)


print(content)

author_ids = []     # 建立一個空的 list 來放作者 id
replies = []        # 建立一個空的 list 來放推文
times = []          # 建立一個空的 list 來放推文時間
tags = []           # 建立一個空的 list 來放推文類型

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


#author_id, author_name, article_title, 
#published_time, contect, artical_url, comment_data