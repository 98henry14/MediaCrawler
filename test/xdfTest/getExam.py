import requests
import json
from concurrent.futures import ThreadPoolExecutor
import re,os,platform


headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "content-type":"application/json",
    "referer": "https://exam.koolearn.com/pc/start-exam?hidden=0&keyId=107346561&platformSn=8426886&terminal=2&extendInfo=8426886_189526&checkSn=1&platform=shark&paperId=224841774407681&sign=37AAA2A98F7213363903C485E49DC0FA",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
cookies = {
    "gr_user_id": "180344aa-0c5b-47de-baf4-c5d6ed529441",
    "MEIQIA_TRACK_ID": "2YANdBOEanSI4CQExSj521lvUlW",
    "MEIQIA_VISIT_ID": "2YANdDjTCWbO3v0KFzaOS5OYY7G",
    "pt_1783e324": "uid=j1K-9XsiTid3maJgpa4icw&nid=1&vid=-GsUeZ5pqcaD5CcwLoRyqA&vn=1&pvn=1&sact=1699964532997&to_flag=0&pl=gjhLyBSjw/HoAfMfeNNUsg*pt*1699964512221",
    "pt_6dc02627": "uid=EnrqXUQe7KYZHIwbgpu1kA&nid=0&vid=Qa9YjXydaEuuiicdACZZ9w&vn=4&pvn=1&sact=1709729416327&to_flag=1&pl=qo36Ue6jIhjoaZD2gbwyxg*pt*1709729062821",
    "9dee9d3e36a527e1_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "kaoyan-0-18804357": "1",
    "kaoyan-0--1": "0",
    "_ga_8RBHSP5JM6": "GS1.2.1716702843.2.0.1716702843.60.0.0",
    "_ga_VE7D9QXBBY": "GS1.2.1716702844.2.0.1716702844.60.0.0",
    "aba0d864c66383b5_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "koo.line": "study",
    "koo-guonei-flowrate-webapp": "4bb2b2cdd12a3864be772b8aad5aaaa0",
    "Hm_lvt_5023f5fc98cfb5712c364bb50b12e50e": "1726661943",
    "HMACCOUNT": "937221BF9BC51C4E",
    "_gid": "GA1.2.1765526487.1726661945",
    "Hm_lpvt_5023f5fc98cfb5712c364bb50b12e50e": "1726661948",
    "mp_ec424f4c03f8701f7226f5a009d90586_mixpanel": "%7B%22distinct_id%22%3A%20%22%24device%3A18e2311e38db57-03b2366ba66a9f-1d525637-1d73c0-18e2311e38db57%22%2C%22%24device_id%22%3A%20%2218e2311e38db57-03b2366ba66a9f-1d525637-1d73c0-18e2311e38db57%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fstudy.koolearn.com%2Fky%2Flearning%2F188924%2F22666338%2F18800053%22%2C%22%24initial_referring_domain%22%3A%20%22study.koolearn.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fstudy.koolearn.com%2Fky%2Flearning%2F188924%2F22666338%2F18800053%22%2C%22%24initial_referring_domain%22%3A%20%22study.koolearn.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D",
    "9dee9d3e36a527e1_gr_session_id": "a617dc71-51ee-44f0-b10e-d8a1a64a118f",
    "9dee9d3e36a527e1_gr_last_sent_sid_with_cs1": "a617dc71-51ee-44f0-b10e-d8a1a64a118f",
    "9dee9d3e36a527e1_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "Qs_lvt_143225": "1719840980%2C1725883186%2C1726316242%2C1726658900%2C1726745113",
    "Qs_pv_143225": "4173547973745649700%2C385773966642047300%2C3950772463349535000%2C4120952658961817000%2C991578409823529300",
    "sso.ssoId": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "ssoSessionID": "A90EAE598B71676046A970A3A4F1BC0C-n2",
    "login_token": "login_token_v2_A90EAE598B71676046A970A3A4F1BC0C-n2",
    "aba0d864c66383b5_gr_session_id": "12dc61ac-9c3c-4aca-943a-f5ce07adf337",
    "aba0d864c66383b5_gr_last_sent_sid_with_cs1": "12dc61ac-9c3c-4aca-943a-f5ce07adf337",
    "_ga": "GA1.1.914741991.1709728842",
    "JSESSIONID": "D95BCBC8CF6B3844278669EDF0335DD4",
    "_ga_MYF8GNFSSR": "GS1.1.1726745111.33.1.1726745442.0.0.0",
    "aba0d864c66383b5_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "gioCookie": "yes"
}
url = "https://exam.koolearn.com/api/exam-process/v1/answer-sheet/226325773955074"

session = requests.session()
response = session.get(url, headers=headers, cookies=cookies)

if platform.system() == "Windows":
    file_path = "C:\\Users\\xiaoj\\Documents\\资料\\xdf"
elif platform.system() == "Darwin":
    file_path = "/Volumes/SandiskSSD/xdf/math/数学2/"
md5_name=""
imgParttern = r'<img.*?src="(.*?)".*?>'
pTagParttern = r'<p>(.*?)</p>'
def downloadImg(img):
    qs = img.group(1)
    imgName = qs.split("/")[-1]
    img = session.get(qs)
    with open(os.path.join(file_path,"img",imgName),'wb') as file:
        file.write(img.content)
    return f"![]({qs})"
def replaceImg(content):
    return re.sub(imgParttern, downloadImg, content)

def fetchContent(content):
    notp = re.findall(pTagParttern,content)
    if notp:
        new_content = ""
        for np in notp:
            new_content = new_content + "" + replaceImg(np)

        return new_content
    else:
        return content
def getDeatil(qs):
    url = "https://exam.koolearn.com/api/question/v1/detail"
    data = {
        "questionId": qs.get("questionId"),
        "questionVersion": "1",
        "queryType": 2
    }
    data = json.dumps(data, separators=(',', ':'))
    response = session.post(url, headers=headers, cookies=cookies, data=data)
    if response.status_code != 200 or response.json().get('status') != 0:
        print("请求失败,",response.json())

    info = response.json().get('data')
    info['questionStem'] = fetchContent(info.get('questionStem'))

    return info

data = response.json().get('data')
print(response.json())
content = []
for mod in data.get('modules'):
    content.append(f"# {mod.get('nodeName')}({mod.get('nodeScore')})")
    index = 0
    for ss in mod.get('structs'):
        content.append(f"## {ss.get('nodeName')}({ss.get('nodeScore')})")
        order = ss.get('nodeOrders')
        qs_list = ss.get("questions")
        qs_map = {item.get('questionId'):item for item in qs_list}
        results = []
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = pool.map(getDeatil,qs_list)
            for result in futures:
                results.append(result)
        new_list = sorted(results,key=lambda x:qs_map.get(x.get("questionId")).get("nodeOrders"))
        for question in new_list:
            index = index+1
            qs = qs_map.get(question.get('questionId'))
            content.append(f"### {index}.{question.get('bizQuestionName')}({qs.get('nodeScore')})")
            content.append(f"{fetchContent(question.get('questionStem'))}")
            for op in question.get("options"):
                for o1 in op:
                    content.append(f"- {o1.get('optionLabel')}.{fetchContent(o1.get('optionValue'))}")

            content.append(f"[^{index}]: {'*'*100}")
            content.append(f"**【标准答案】：{question.get('standardAnswer')} **")
            for ans in question.get("analysis"):
                for a1 in ans :
                    if a1.get('analysisValue'):
                        content.append(f"{fetchContent(a1.get('analysisValue'))}")
            content.append("***")

if content:
    with open(os.path.join(file_path,f"{data.get('paperName')}.md"),'w',encoding="utf-8") as file:
        file.write("\n".join(content))

