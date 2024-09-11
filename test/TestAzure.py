#!/opt/homebrew/Frameworks/Python.framework/Versions/3.9/bin/
# -*- codig:utf-8 -*-

import base64
import datetime
import subprocess
import threading

import requests
from urllib.parse import urlparse, parse_qs

import json
import os
# import pycryptodome
from Crypto.Cipher import AES
from concurrent.futures import ThreadPoolExecutor, as_completed

# mac
ffmpeg_path="/Users/xiexiaojie/Downloads/ffmpeglib/ffmpeg"
dir_path = "/Volumes/SandiskSSD/python-project/pythonSpider/图灵爬虫/static"
old_m3u8_path = f"{dir_path}/old.m3u8"
ts_path = f"{dir_path}/m3u8"
new_index_m3u8 = "index.m3u8"
new_m3u8_path = f"{ts_path}/{new_index_m3u8}"
merge_video_name = "Day 06-修饰集团-之状语精讲-1.mp4"

# win
# ffmpeg_path="/Users/xiexiaojie/Downloads/ffmpeglib/ffmpeg"
# dir_path = "C:\\Users\\xiaoj\\Downloads"
# old_m3u8_path = f"{dir_path}\\ceshi.m3u8"
# ts_path = f"{dir_path}\\m3u8"
# new_index_m3u8 = "index-2.m3u8"
# new_m3u8_path = f"{ts_path}\\{new_index_m3u8}"
# merge_video_name = "hello.mp4"


def run_azure_command(command):
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return None


# r1 = subprocess.run("az --version", check=True, shell=True, stdout=subprocess.PIPE,  text=True)
# if r1:
#     print(r1.stdout.strip())
# # print(run_azure_command("az --version"))
# print(run_azure_command("az cloud set -n AzureChinaCloud"))
# # print(run_azure_command("az login -u xie.xj.17@pg.com -p Tsc745159!jet"))
# cmd = "az ad user list --query [].userPrincipalName --output tsv"
# res = run_azure_command(cmd)
# if res:
#     print("执行aure")
#     print(res.split("\n"))


# # 从本地读取m3u8文件，获取ts连接并下载
def read_m3u8_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    ts_urls = []
    key_url = ""
    # 同时写入新的文件里面
    if not os.path.exists(ts_path):
        os.mkdir(ts_path)
    index = open(new_m3u8_path, "w")
    for line in lines:

        if line.startswith('#'):
            if line.startswith('#EXT-X-KEY:'):
                key_url = line.split(',')[1].strip().replace("URI=", "").replace("\"", "")
            else:
                index.write(line)
            continue
        index.write(f"{ts_path}{os.path.sep}{line.split('?')[0]}\n")
        ts_urls.append(line.strip())
    return key_url, ts_urls


def decrypt_key(raw_content, token):
    print(raw_content)

    tk = json.loads(base64.b64decode(token))
    print(tk)
    key = tk['key']
    newR = []
    for d in dt:
        newR.append(d ^ key)
    return bytes(newR)


# 从本地读取m3u8文件，并提取
kurl, res = read_m3u8_file(old_m3u8_path)
print(res)

# os.system("az --version")


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

# 解析key的 URL
parsed_url = urlparse(kurl)

# 提取查询参数
query_params = parse_qs(parsed_url.query)

# 打印提取的参数
print("原始URL:", kurl)
print("解析后的URL:", parsed_url)
print("查询参数:", query_params)
vid = query_params['vid'][0]

# 提取key，并获取最终解密的key
resp = requests.get(kurl, headers=headers, stream=True)
resp.raw.decode_content = True
dt = resp.raw.read()
kb = decrypt_key(dt, query_params['MtsHlsUriToken'][0])
# okb = [59,223,20,27,102,158,210,1,199,119,114,66,238,119,185,46]
# kb = bytes(okb)
print(kb)
ib = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

"""
iv 的加密方式如下，问题 A 从哪里来，貌似都回累计加1，
A.prototype.createInitializationVector = function(A) {
    for (var t = new Uint8Array(16), e = 12; e < 16; e++)
        t[e] = A >> 8 * (15 - e) & 255;
    return t
}

key的取值
1.从m3u8中获取到加密地址uri，调用 并获得二进制数组,byteArr
2.提取uri中MtsHlsUriToken的值，通过base64解析为json，再提取其中key
3.将获得二进制数组byteArr逐位跟key进行 ^ 异或操作，最终结果就是kb


"""


def download_ts(re):
    url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/{vid}/{re}"
    urlsplit = re.split("?")
    response = requests.get(url, headers=headers)
    # print(response)
    desc = AES.new(kb, AES.MODE_CBC, ib).decrypt(response.content)
    with open(os.path.join(ts_path , urlsplit[0]),
              mode="wb") as f3:
        f3.write(desc)
    print("{}->file './{}'".format(threading.currentThread().getName(), urlsplit[0]))
    return True


start = datetime.datetime.now()
task = []
print("使用多线程方式下载ts文件")
with ThreadPoolExecutor(max_workers=50) as executor:
    # results = executor.map(download_ts,res)
    task.extend([executor.submit(download_ts, ts) for ts in res])
    print("任务总数",len(task))

as_completed(task,timeout=10)
print("使用多线程方式下载ts文件完成,耗时",datetime.datetime.now()-start)
# 任务总数 23,使用多线程方式下载ts文件完成,耗时 0:01:06.389875
# 在 mac 中，任务总数 307 使用多线程方式下载ts文件完成,耗时 0:00:11.347175

# 如果不使用多线程执行的话
# print("循环下载ts文件")
# for re in res:
#     download_ts(re)
# print("循环下载ts文件完成,耗时", datetime.datetime.now() - start)
# 任务总数 23 循环下载ts文件完成,耗时 0:00:48.333951




# os.chdir(dir_path+"m3u8")
# os.system("ffmpeg -i index.m3u8 -c copy new1.mp4")
# run_azure_command(f"cd {ts_path}")
# run_azure_command(f"cd {ts_path}; ffmpeg -i {new_index_m3u8} -c copy {merge_video_name}")
os.chdir(ts_path)
os.system(f"ffmpeg -i {new_index_m3u8} -c copy {merge_video_name}")
# import csv
#
# # res = os.system("az ad user list --filter \"userPrincipalName eq 'xie.xj.17@pg.com'\" --query [].userPrincipalName --output tsv")
#
# def run_azure_command(command):
#     try:
#         result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         print(f"Error running command: {e}")
#         return None
# res = run_azure_command("az ad user list --filter \"userPrincipalName eq 'xie.xj.17@pg.com' or userPrincipalName eq 'chen.x.100@pg.com'\" --query [].userPrincipalName --output tsv")
# with open("C:\\Users\\xiaoj\\Desktop\\usercheck\\ad_users-3.csv", mode="w",newline='',encoding="utf-8") as ff:
#     write = csv.writer(ff)
#     # print(res)
#     print(res.split("\n"))
#     print([[line] for line in res.split("\n")])
#     # for a in res.split("\n"):
#     #     write.writerow([a])
#     # write.writerow(res)
#     write.writerows([[line] for line in res.split("\n")])