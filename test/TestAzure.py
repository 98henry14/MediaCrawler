import base64
import datetime
import subprocess


import requests
from urllib.parse import urlparse, parse_qs

import json
import os
import shutil
# import pycryptodome
from Crypto.Cipher import AES
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import platform
import redis
import re

r = redis.Redis(host='localhost', port=6379, db=0)


sys = platform.system()
if sys == "Darwin":
# mac
    ffmpeg_path="/Users/xiexiaojie/Downloads/ffmpeglib/ffmpeg"
    # dir_path = "/Volumes/SandiskSSD/python-project/pythonSpider/图灵爬虫/static"
    # old_m3u8_path = f"{dir_path}/old.m3u8"
    # ts_path = f"{dir_path}/m3u8"
    # new_index_m3u8 = "index.m3u8"
    # new_m3u8_path = f"{ts_path}/{new_index_m3u8}"
    # merge_video_name = "Day 06-修饰集团-之状语精讲-1.mp4"
    file_path = "/Volumes/SandiskSSD/xdf/math/数学2"
    assign_path = "/Volumes/SandiskSSD/xdf/m3u8folder"
    move_path = "/Volumes/SandiskSSD/xdf/special"
elif sys == "Windows":
    # win
    ffmpeg_path = "C:\\Users\\xiaoj\\software\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"
    # dir_path = "C:\\Users\\xiaoj\\Downloads"
    # old_m3u8_path = f"{dir_path}\\ceshi.m3u8"
    # ts_path = f"{dir_path}\\m3u8"
    # new_index_m3u8 = "index-2.m3u8"
    # new_m3u8_path = f"{ts_path}{os.path.sep}{new_index_m3u8}"
    # merge_video_name = "hello.mp4"
    file_path = "C:\\Users\\xiaoj\\baidusync\\xdf\\math\\数学2\\"
    assign_path = "C:\\Users\\xiaoj\\baidusync\\xdf\\math\\数学2\\"
    move_path = "C:\\Users\\xiaoj\\baidusync\\xdf\\math\\数学2\\"
elif sys == "Linux":
    ffmpeg_path =""
    merge_video_name =""
    file_path = ""
else:
    print("系统不支持")
    exit()






def run_azure_command(command):
    try:
        result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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

    # index = open(new_m3u8_path, "w")
    content = []
    for line in lines:
        if line.startswith('#'):
            if line.startswith('#EXT-X-KEY:'):
                key_url = line.split(',')[1].strip().replace("URI=", "").replace("\"", "")
            else:
                # index.write(line)
                content.append(line)
            continue
        # index.write(f"{os.path.sep}{line.split('?')[0]}\n")
        content.append(f"{os.path.sep}{line.split('?')[0]}\n")
        ts_urls.append(line.strip())
    return key_url, ts_urls ,content

def generate_new_m3u8_file(final_path,new_index_name,content):
    new_m3u8_path = os.path.join(final_path, new_index_name)
    with open(new_m3u8_path,"w") as newfile:
        if content:
            for line in content:
                if not line.startswith("#"):
                    line = f"{final_path}{line}"
                newfile.write(line)


def decrypt_key(raw_content, token):
    print(raw_content)

    tk = json.loads(base64.b64decode(token))
    print(tk)
    key = tk['key']
    newR = []
    for d in raw_content:
        newR.append(d ^ key)
    return bytes(newR)






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

def download_ts(ts_name, vid, kb, ib, final_path):
    urlsplit = ts_name.split("?")
    # 这个地方还是变化蛮大的，还是要从 getmvediourl获取到具体的前缀
    if re.search(r"^[A-Z0-9\-]+.ts$", urlsplit[0]):
        url = f"https://media-editor.roombox.xdf.cn/{vid}/transcode/normal/{ts_name}"
    else:
        url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/{vid}/{ts_name}"
    response = requests.get(url, headers=headers)
    if not response.status_code == 200:
        # 再尝试通过这个地址获取看看，如果没有报错
        url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/roombox/10/{vid}/{ts_name}"
        # url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/{vid}/{ts_name}"
        r2 = requests.get(url, headers=headers)
        if not r2.status_code == 200:
            print(f"获取 ts 文件请求失败，url={url},返回：{r2.text}")
            return

    # print(threading.currentThread().getName(),"调用ts 接口返回",response)
    desc = AES.new(kb, AES.MODE_CBC, ib).decrypt(response.content)
    ts_file =os.path.join(final_path , urlsplit[0])
    if not os.path.exists(ts_file):
        with open(ts_file,mode="wb") as f3:
            f3.write(desc)
        print("{}->file './{}'".format(threading.currentThread().getName(), urlsplit[0]))
    else:
        print("本地存在ts文件不执行解密下载，",ts_file)
    return urlsplit[0]



def download_accord_local_m3u8(filename):
    file = os.path.join(assign_path, filename)
    if os.path.isfile(file) and filename.endswith("m3u8") and not filename.startswith("._"):
        kurl, res, content = read_m3u8_file(file)

        # 解析key的 URL
        parsed_url = urlparse(kurl)

        # 提取查询参数
        query_params = parse_qs(parsed_url.query)
        vid = query_params['vid'][0]

        # 从 redis 获取匹配数据
        info = r.hget(f"xdf:video:pathid_344056", vid)
        if info:
            info = json.loads(info)
            print(info)
            generate_mp4_address = info.get('generate_mp4_address')
            if not generate_mp4_address:
                path = info.get('pathName')
                id = info.get('id')
                final_path = os.path.join(file_path, path)
                new_idx_m3u8_name = f"{id}_la.m3u8"
                local_m3u8 = os.path.join(final_path, new_idx_m3u8_name)

                mp4 = info.get('name') + ".mp4"
                merge_mp4_name = os.path.join(final_path, mp4)

                generate_new_m3u8_file(final_path, new_idx_m3u8_name, content)

                # 提取key，并获取最终解密的key
                resp = requests.get(kurl, headers=headers, stream=True)
                resp.raw.decode_content = True
                dt = resp.raw.read()
                kb = decrypt_key(dt, query_params['MtsHlsUriToken'][0])
                # okb = [59,223,20,27,102,158,210,1,199,119,114,66,238,119,185,46]
                # kb = bytes(okb)
                print(kb)
                ib = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

                start = datetime.datetime.now()
                task = []
                print("使用多线程方式下载ts文件")
                with ThreadPoolExecutor(max_workers=20) as executor:
                    # results = executor.map(download_ts,res)
                    task.extend(
                        [executor.submit(download_ts, ts_name=ts, vid=vid, kb=kb, ib=ib, final_path=final_path) for ts in
                         res])
                    print("任务总数", len(task))

                as_completed(task, timeout=10)

                ts_file_list = [t.result() for t in task]
                if any(ts in [None] for ts in ts_file_list):
                    print("存在文件下载失败，无法合并")
                    exit()

                print(f"使用多线程方式下载ts文件完成,文件内容列表为{ts_file_list}\n耗时:{datetime.datetime.now() - start}")
                # 任务总数 23,使用多线程方式下载ts文件完成,耗时 0:01:06.389875
                # 在 mac 中，任务总数 307 使用多线程方式下载ts文件完成,耗时 0:00:11.347175

                # 如果不使用多线程执行的话
                # print("循环下载ts文件")
                # for re in res:
                #     download_ts(re)
                # print("循环下载ts文件完成,耗时", datetime.datetime.now() - start)
                # 任务总数 23 循环下载ts文件完成,耗时 0:00:48.333951
                # 任务总数 249 循环下载ts文件完成,耗时 0:06:17.746527

                # os.chdir(dir_path+"m3u8")
                # os.system("ffmpeg -i index.m3u8 -c copy new1.mp4")
                r1 = run_azure_command(f"cd '{final_path}'")
                r2 = run_azure_command(f" {ffmpeg_path} -i '{local_m3u8}' -c copy '{merge_mp4_name}' -y")
                # print(r1)
                print(r2)
                del_file_list = "' '".join(ts_file_list)
                r3 = run_azure_command(f"cd '{final_path}' && rm -rf '{del_file_list}' ")
                # print(r3)
                info['generate_mp4_address'] = merge_mp4_name
                shutil.move(file,os.path.join(move_path,filename))
                r.hset(f"xdf:video:pathid_344056", vid, json.dumps(info, ensure_ascii=False))
            else:
                shutil.move(file, os.path.join(move_path, filename))
                print(f"vid:{vid}已经生成过文件，跳过.地址:{generate_mp4_address}" )
            # 删除文件
            # os.chdir(final_path)
            # os.system(f"{ffmpeg_path} -i {local_m3u8} -c copy {merge_video_name}")
        else:
            print("未从 redis 中找到匹配数据，video id:", vid)


# 同时写入新的文件里面
if not os.path.exists(assign_path):
    os.mkdir(assign_path)

ks = datetime.datetime.now()
# with ThreadPoolExecutor(max_workers=5) as exe:
#     exe.map(download_accord_local_m3u8, os.listdir(assign_path))
for file in os.listdir(assign_path):
    download_accord_local_m3u8(file)


print("总耗时:",datetime.datetime.now()-ks)


