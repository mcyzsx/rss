# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser

######################################################################################
displayDay=7 # 抓取多久前的内容
displayMax=2 # 每个RSS最多抓取数
weeklyKeyWord="" # 周刊过滤关键字

rssBase={
    "安知鱼":{
        "url":"https://blog.anheyu.com/rss.xml",
        "type":"post",
        "timeFormat":"%a, %d %b %Y %H:%M:%S GMT",
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
        "timeFormat":"%a, %d %b %Y %H:%M:%S GMT",
        "nameColor":"#df7150"
    }
}
######################################################################################

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
    retries = 3
    success = False
    
    while retries > 0 and not success:
        try:
            rssDate = feedparser.parse(rssBase[rss]["url"])
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
                        time_formats = [rssBase[rss]["timeFormat"], "%a, %d %b %Y %H:%M:%S GMT", "%a, %d %b %Y %H:%M:%S +0000"]
                    
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
            
            success = True  # Mark as successful if we got through parsing
        except Exception as e:
            print("Error: Failed to parse RSS feed for %s. Error message: %s"%(rss, str(e)))
            retries -= 1
            if retries > 0:
                print("====== Retrying (%d attempts left) ======"%retries)
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                print("====== All retries failed, skipping this feed ======")
            continue

            
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
