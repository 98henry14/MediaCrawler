import time

import requests
# 旧线程模块
import _thread
# 新的线程模块
import threading


# def run(i):
#     print(f"Thread {i} running \n")
#
# for i in range(5):
#     _thread.start_new_thread(run, (i,))
#
# print("先执行哪个？")

def run2():
    print("执行run2,当前线程名称:",threading.current_thread().name)
    for i in range(10):
        print(i,'==========')
        time.sleep(1)
# for i in range(5):
#     _thread.start_new_thread(run2, ())
#
# for i in range(10):
#     time.sleep(1)
#
# print("xxxxx")

mt = threading.Thread(target=run2,name="thread2")
mt.start()


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-cache",
    "origin": "https://study.koolearn.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://study.koolearn.com/ky/learning/188924/22666338/19725417",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
url = "https://media-editor.roombox.xdf.cn/clouddriver-transcode/5bf82ce0eda271ee9452f6e7d7696302/7fe74586e09c45a8a65e45ea0e2ec19c-00001.ts"
params = {
    "auth_key": "1726318708-d837203db925427b8576e8adec33e6d7-0-fa96b7c010b86635fc89962135d54425"
}
response = requests.get(url, headers=headers, params=params)

print(response.text)
print(response)