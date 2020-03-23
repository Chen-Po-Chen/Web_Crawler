# crawler_ptt

### System

OS: Windows10
Code: Python3.7.0

### Intro

ptt web 的網路爬蟲，並能指定欲擷取的貼文發佈日期區間，若遇到已擷取過的，網址因避免浪費資源而重複擷取。
可擷取作者ID、作者暱稱、標題、內文、貼文時間、標網址、發文時間、推文者ID、推文內容、推文時間的資訊。

資料儲存位置分為local以及SQL資料庫
- crawler.py
  - 將資料上傳至MySQL資料庫
  - 注意:資料庫資訊需修改
    - SERVER_INFO = ["localhost",			 # IP
				             "root",				   # User Name
				             "*****",			     # Password
				             "ptt_hot_article"]# Database Name
- crawler_local.py
  - 將資料儲存在本地電腦裡
    - 以.npy檔案儲存
  - 注意：存放路徑
    - SAVE_DATA_ROOT = "C:/Users/Po-Chen/Documents/PTT/"
    
### Download and Run

打開cmd並到下載的檔案路徑下

下載需要用的modules
pip install -r requirment.txt

執行程式
python crawler.py
