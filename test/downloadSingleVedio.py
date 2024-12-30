import subprocess
import requests
import urllib,json,base64
from Crypto.Cipher import AES

import os,platform
import shlex
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed



def extract_m3u8_content( text):
    """
    调用 m3u8 的文件接口，根据返回的内容提取解密 key、ts 文件的地址、自定义地址内容
    """
    ts_urls = []
    key_url = ""
    content = []
    for line in text.split("\n"):
        if not line.strip():
            continue
        if line.startswith('#'):
            if line.startswith('#EXT-X-KEY:'):
                key_url = line.split(',')[1].strip().replace("URI=", "").replace("\"", "")
            else:
                content.append(f"{line}\n")
            continue
        content.append(f"{os.path.sep}{line.split('?')[0]}\n")
        ts_urls.append(line.strip())
    return key_url, ts_urls, content


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,sq;q=0.6,pl;q=0.5",
    "cache-control": "no-cache",
    "origin": "https://study.koolearn.com",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://study.koolearn.com/ky/learning/189526/22666340/19267158",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}
origin_url = "https://media-editor.roombox.xdf.cn/clouddriver-transcode/roombox/3/230bb070171771efb974f6e7d7696302/f63718d0d5d34ae1bacc3c699d32f4f5.m3u8?MtsHlsUriToken=eyJ0aW1lIjoxNzM1NDUxOTY0LCJ0b2tlbiI6ImY3ZTAzZWU2OGRjN2RjOWQ4OTY0NzIxMmI0OGZkMTJkIiwia2V5Ijo1MCwiZW5jX3R5cGUiOjIsInVybF90eXBlIjoxLCJkZWZpbml0aW9uIjoiSEQiLCJzdHJlYW1fdHlwZSI6InZpZGVvIiwiYXBwX2lkIjoicm9vbWJveCIsIkNhdGVnb3J5SWQiOjN9&auth_key=1735970364-71655ac81fb8408ebc0754b9550b02fa-0-5552f1741756b46c5b00b9d1561eb9cb"


url = origin_url.split('?')[0]
omap = origin_url.split('?')[1]
params={}
for i in omap.split('&'):
    params.update({i.split("=")[0]: i.split("=")[1]})
# params = {
#     "MtsHlsUriToken": "eyJ0aW1lIjoxNzM1NDUyNTgzLCJ0b2tlbiI6ImJmMzAwOTk5ZDI5NTU2MTA2ZThmYzEwZTdhNmJhNjdiIiwia2V5IjoyOSwiZW5jX3R5cGUiOjIsInVybF90eXBlIjoxLCJkZWZpbml0aW9uIjoiU0QiLCJzdHJlYW1fdHlwZSI6InZpZGVvIiwiYXBwX2lkIjoia29vbGVhcm5fMTAwMjAwMSIsIkNhdGVnb3J5SWQiOjN9",
#     "auth_key": "1735970983-d00a8be4a69445d8b9475d53be417385-0-6dda41a98f49b5564eddda31adce749e"
# }
print(params)
final_path = "/Volumes/SandiskSSD/xdf/2025考研英语全程班 春季班/强化刷题（经典真题）/写作经典真题（英语二）/写作经典真题讲解/潘赟"
ffmpeg_path = "/Users/xiexiaojie/Downloads/ffmpeglib/ffmpeg"
urllist = url.split("/")
merge_mp4_name=f"{final_path}/全篇刷题-图画经典整篇.mp4"
qt = "\"" if platform.system() == "Windows" else "'"
# ts_url_prefix = urllist[:-2]
ts_url_prefix = "https://media-editor.roombox.xdf.cn/clouddriver-transcode/roombox/3/230bb070171771efb974f6e7d7696302"

print(ts_url_prefix)

# 第一步，获取m3u8文件，提取ts内容及key内容
ss = requests.session()
response = ss.get(url, headers=headers, params=params)
key_url, ts_urls, content = extract_m3u8_content(response.text)

# 第二步，提取key内容
resp = ss.get(key_url, headers=headers, stream=True)
resp.raw.decode_content = True
dt = resp.raw.read()

tk = json.loads(base64.b64decode(params.get('MtsHlsUriToken')))
print(tk)
key = tk['key']
newR = []
for d in dt:
    newR.append(d ^ key)
kb = bytes(newR)
ib = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

new_m3u8_path = os.path.normpath(os.path.join(final_path, "new.m3u8"))
# os.makedirs(final_path, exist_ok=True)
with open(new_m3u8_path, "w") as newfile:
    if content:
        for line in content:
            if not line.startswith("#"):
                line = f"{final_path}{line}"
            newfile.write(line)
def download_ts(ts_name, kb, ib, final_path ):
    """
    下载ts文件
    """
    ts_url = f"{ts_url_prefix}/{ts_name}"
    res = ss.get(ts_url, headers=headers)
    ts_file = os.path.join(final_path, ts_name.split('?')[0])
    if os.path.exists(ts_file):
        return
    try:
        desc = AES.new(kb, AES.MODE_CBC, ib).decrypt(res.content)
    except Exception as e:
        print(f"解密失败，,ts={ts_name},错误信息：{e}")
        raise
    with open(ts_file, mode="wb") as f3:
        f3.write(desc)

# 第三步，批量下载ts文件
loop = asyncio.get_event_loop()
executor = ThreadPoolExecutor(max_workers=30)
task = [loop.run_in_executor(executor,asyncio.run,download_ts(ts_name=ts,kb=kb,ib=ib,final_path=final_path)) for ts in ts_urls]
ts_file_list = as_completed(task)
print("任务总数", len(task), "开始下载ts文件")


generate_command = f"{ffmpeg_path} -i {qt}{new_m3u8_path}{qt} -c copy {qt}{merge_mp4_name}{qt} -y"

try:
    result = subprocess.run(generate_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)
    print(result.stdout.strip())
except subprocess.CalledProcessError as e:
    print(f"Error running command: {e}")

ts_file_list = [f"{final_path}/{ts_name.split('?')[0]}" for ts_name in ts_urls]

del_file_list = "' '".join(ts_file_list)
del_command = f"cd {qt}{final_path}{qt} && rm -rf {qt}{del_file_list}{qt} "

try:
    result = subprocess.run(del_command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)
    print(result.stdout.strip())
except subprocess.CalledProcessError as e:
    print(f"Error running command: {e}")
