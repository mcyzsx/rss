# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from io import BytesIO

######################################################################################
displayDay=7 # 抓取多久前的内容
displayMax=2 # 每个RSS最多抓取数
weeklyKeyWord="" # 周刊过滤关键字

rssBase={
    "安知鱼":{
        "url":"https://blog.anheyu.com/rss.xml",
        "type":"post",
        "timeFormat":"%a, %d %b %Y %H:%M:%S +0000",
        "nameColor":"#a4244b"
    },
    "张洪heo":{
        "url":"https://blog.zhheo.com/rss.xml",
        "type":"post",
        "timeFormat":"%a, %d %b %Y %H:%M:%S GMT",
        "nameColor":"#b8d101"
    },
    "纸鹿":{
        "url":"https://blog.zhilu.site/atom.xml",
        "type":"post",
        "timeFormat":"%Y-%m-%dT%H:%M:%SZ",
        "nameColor":"#e76976"
    },
    "APP喵":{
        "url":"https://www.appmiao.com/feed",
        "type":"post",
        "timeFormat":"%a, %d %b %Y %H:%M:%S +0000",
        "nameColor":"#93bd76"
    },
    "Meekdai":{
        "url":"https://blog.meekdai.com/rss.xml",
        "type":"post",
        "timeFormat":"%a, %d %b %Y %H:%M:%S +0000",
        "nameColor":"#df7150"
    }
}
######################################################################################

def fetch_rss_with_requests(url, retries=3):
    """使用 requests 库获取 RSS 内容，支持自定义请求头"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=30, verify=True)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print("====== Request attempt %d failed: %s ======" % (attempt + 1, str(e)))
            if attempt < retries - 1:
                time.sleep(2)
            else:
                raise e
    return None

rssAll=[]
info=json.loads('{}')
info["published"]=int(time.time())
info["rssBase"]=rssBase
rssAll.append(info)

displayTime=info["published"]-displayDay*86400

print("====== Now timestamp = %d ======"%info["published"])
print("====== Start reptile Last %d days ======"%displayDay)

for rss in rssBase:
    print("====== Reptile %s ======"%rss)
    rssDate = None
    
    # 尝试使用 requests 获取 RSS 内容
    try:
        rss_content = fetch_rss_with_requests(rssBase[rss]["url"])
        rssDate = feedparser.parse(BytesIO(rss_content))
        print("====== Using requests to fetch RSS ======")
    except Exception as req_e:
        print("====== Requests failed: %s ======" % str(req_e))
        print("====== Trying feedparser directly ======")
    
    # 如果 requests 失败，使用 feedparser 直接解析
    if rssDate is None or not rssDate.get('entries'):
        try:
            rssDate = feedparser.parse(rssBase[rss]["url"])
            print("====== Using feedparser directly ======")
        except Exception as fp_e:
            print("====== Feedparser also failed: %s ======" % str(fp_e))
            print("====== Skipping this feed ======")
            continue
    
    # 检查是否获取到数据
    if not rssDate or not rssDate.get('entries'):
        print("====== No entries found for %s ======" % rss)
        continue
    
    print("====== Feed status: %s ======"%rssDate.get('status', 'unknown'))
    print("====== Number of entries: %d ======"%len(rssDate.get('entries', [])))
    
    # Check for common date keys in entries
    if rssDate.get('entries'):
        first_entry = rssDate['entries'][0]
        print("====== Available date keys in first entry: %s ======"%list(key for key in first_entry if 'date' in key.lower() or 'publish' in key.lower()))
        
        # Print all available keys for debugging
        print("====== All keys in first entry: %s ======"%list(first_entry.keys()))
    
    i=0
    for entry in rssDate['entries']:
        if i>=displayMax:
            break
        
        # Try different date fields
        date_field = None
        if 'published' in entry:
            date_field = 'published'
        elif 'pubdate' in entry:
            date_field = 'pubdate'
        elif 'date' in entry:
            date_field = 'date'
        elif 'updated' in entry:
            date_field = 'updated'
        
        if date_field:
            print("====== Using date field: %s ======"%date_field)
            print("====== Entry date: %s ======"%entry[date_field])
            
            # Try multiple time formats for each feed
            time_formats = []
            if rss == "纸鹿":
                time_formats = ["%Y-%m-%dT%H:%M:%SZ", "%a, %d %b %Y %H:%M:%S GMT", "%a, %d %b %Y %H:%M:%S +0000"]
            else:
                # Create a unique list of formats to try
                base_format = rssBase[rss]["timeFormat"]
                time_formats = [base_format]
                
                # Add GMT format if not already included
                if "%a, %d %b %Y %H:%M:%S GMT" not in time_formats:
                    time_formats.append("%a, %d %b %Y %H:%M:%S GMT")
                
                # Add +0000 format if not already included
                if "%a, %d %b %Y %H:%M:%S +0000" not in time_formats:
                    time_formats.append("%a, %d %b %Y %H:%M:%S +0000")
            
            published = None
            for fmt in time_formats:
                try:
                    print("====== Trying format: %s ======"%fmt)
                    published=int(time.mktime(time.strptime(entry[date_field], fmt)))
                    print("====== Parsed timestamp: %d ======"%published)
                    break
                except Exception as fmt_e:
                    print("====== Format %s failed: %s ======"%(fmt, str(fmt_e)))
                    continue
            
            if published is None:
                print("====== All time formats failed, skipping entry ======")
                continue
            
            # Skip timezone adjustment for GMT and Z formats
            if entry[date_field][-5]=="+" and "GMT" not in entry[date_field] and "Z" not in entry[date_field]:
                published=published-(int(entry[date_field][-5:])*36)
                print("====== Adjusted timestamp: %d ======"%published)
            
            if rssBase[rss]["type"]=="weekly" and (weeklyKeyWord not in entry['title']):
                continue
            
            if published>info["published"]:
                print("====== Entry too new, skipping ======")
                continue
            
            if published>displayTime:
                onePost=json.loads('{}')
                onePost["name"]=rss
                onePost["title"]=entry['title']
                onePost["link"]=entry['link']
                onePost["published"]=published
                rssAll.append(onePost)
                print("====== Reptile %s ======"%(onePost["title"]))
                i=i+1
            else:
                print("====== Entry too old, skipping ======")
        else:
            published = None
            print("Warning: No date field found in entry")
    
    # Check if no entries were pulled
    if i == 0 and rssDate.get('entries'):
        print("====== No recent entries found for %s (last 7 days) ======"%rss)

            
print("====== Start sorted %d list ======"%(len(rssAll)-1))
rssAll=sorted(rssAll,key=lambda e:e.__getitem__("published"),reverse=True)

if not os.path.exists('docs/'):
    os.mkdir('docs/')
    print("ERROR Please add docs/index.html")

listFile=open("docs/rssAll.json","w")
listFile.write(json.dumps(rssAll))
listFile.close()
print("====== End reptile ======")
######################################################################################
