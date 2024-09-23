import subprocess
import requests
import urllib
import pycryptodome

import os


# def run_azure_command(command):
#     try:
#         result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         print(f"Error running command: {e}")
#         return None
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
    for line in lines:
        if line.startswith('#'):
            continue
        ts_urls.append(line.strip())
    return ts_urls

res = read_m3u8_file("./static/old.m3u8")
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
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
url = "https://media-vod.roombox.xdf.cn/v1/play/decrypt"
params = {
    "Ciphertext": "N2FiYzViMmUtZjJhNi00YzdhLThjYWUtZjY3Yzk2MWZmZmJmZU9uand6VUdGTHhPd1lYb2IrUEFGTnJCMytHWEpFNnZBQUFBQUFBQUFBRFBkaXN3aWQwVjQ5Qy84cG04cTRJZXZGcTJxR2hVWTFnOGlaNDVZOWVqY0xSU2tpZDl2UmIx",
    "vid": "5bf82ce0eda271ee9452f6e7d7696302",
    "KeyServiceType": "KMS",
    "FromService": "Roombox",
    "MtsHlsUriToken": "eyJ0aW1lIjoxNzI2MDU2NzM3LCJ0b2tlbiI6IjAxNDI5MThlN2U1MDAwMjU0NGVlNmRhYzFiMjk5NWU3Iiwia2V5IjoyMzUsImVuY190eXBlIjoyLCJ1cmxfdHlwZSI6MSwiZGVmaW5pdGlvbiI6IlNEIiwic3RyZWFtX3R5cGUiOiJ2aWRlbyIsImFwcF9pZCI6Imtvb2xlYXJuXzEwMDIwMDEiLCJDYXRlZ29yeUlkIjozfQ=="
}
key = requests.get(url, headers=headers, params=params).content
print(key)
iv = b'0000000000000000'

# with open("C:\\Users\\xiaoj\\Downloads\\m3u8\\decrypt",mode="wb") as f:
#     url="https://media-vod.roombox.xdf.cn/v1/play/decrypt"
#     params = {
#         "Ciphertext": "N2FiYzViMmUtZjJhNi00YzdhLThjYWUtZjY3Yzk2MWZmZmJmZU9uand6VUdGTHhPd1lYb2IrUEFGTnJCMytHWEpFNnZBQUFBQUFBQUFBRFBkaXN3aWQwVjQ5Qy84cG04cTRJZXZGcTJxR2hVWTFnOGlaNDVZOWVqY0xSU2tpZDl2UmIx",
#         "vid": "5bf82ce0eda271ee9452f6e7d7696302",
#         "KeyServiceType": "KMS",
#         "FromService": "Roombox",
#         "MtsHlsUriToken": "eyJ0aW1lIjoxNzI2MDM2MDEzLCJ0b2tlbiI6ImM2ZDkwYzY1MTg2NTc0OTBiYjNkYWRkYjMwOWMzNzE4Iiwia2V5Ijo2MywiZW5jX3R5cGUiOjIsInVybF90eXBlIjoxLCJkZWZpbml0aW9uIjoiU0QiLCJzdHJlYW1fdHlwZSI6InZpZGVvIiwiYXBwX2lkIjoia29vbGVhcm5fMTAwMjAwMSIsIkNhdGVnb3J5SWQiOjN9"
#     }
#     resp = requests.get(url, headers=headers, params=params , verify=False)
#     f.write(resp.content)

with open("C:\\Users\\xiaoj\\Downloads\\m3u8\\file2.txt", mode="w") as f:
    for re in res:
        url =f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/5bf82ce0eda271ee9452f6e7d7696302/{re}"
        urlsplit = re.split("?")
        response = requests.get(url, headers=headers)
        # print(response)
        aes = AES.new(key=key,mode=AES.MODE_CBC,iv=iv)
        desc_data = aes.decrypt(response.content)
        with open(os.path.join("./static", urlsplit[0]),
                  mode="wb") as f3:
            f3.write(desc_data)
        print("file './{}'\n".format( urlsplit[0]))
        f.write("file './{}'\n".format( urlsplit[0]))
    # print(response.text)

ts_path="C:\\Users\\xiaoj\\Downloads\\m3u8\\"
os.system(f"ffmpeg -f concat -safe 0 -i {ts_path}file.txt -c copy {ts_path}video.mp4")
