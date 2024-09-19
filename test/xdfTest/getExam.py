import requests
import json
from concurrent.futures import ThreadPoolExecutor
import re,os


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
    "gr_user_id": "ccb32893-c33e-44d3-bf15-de1537360181",
    "aba0d864c66383b5_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "Qs_lvt_143225": "1725696856",
    "9dee9d3e36a527e1_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "easeMobId": "koolearn1725712051456838882",
    "easeMobPassword": "koolearn1725712051456838882",
    "MEIQIA_TRACK_ID": "2lk77SJE9RG8hKuAacDrqVEVqZA",
    "MEIQIA_VISIT_ID": "2lk77SeWZjOACKj4nxhNC30VZN8",
    "Qs_pv_143225": "2416550789484732400%2C2619313347871156000%2C1671800531537438000%2C1672103693951368400",
    "_ga": "GA1.1.993296956.1713625335",
    "9dee9d3e36a527e1_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "_ga_MYF8GNFSSR": "GS1.1.1726104294.6.0.1726104294.0.0.0",
    "Hm_lvt_5023f5fc98cfb5712c364bb50b12e50e": "1725332527,1726036134,1726639980",
    "HMACCOUNT": "34DEDCD166447D6D",
    "koo.line": "study",
    "sso.ssoId": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "ssoSessionID": "F9FE5D78C807EFA348A00D213654B745-n1",
    "login_token": "login_token_v2_F9FE5D78C807EFA348A00D213654B745-n1",
    "aba0d864c66383b5_gr_session_id": "e41a4e28-a166-4676-80af-53221185ba9d",
    "aba0d864c66383b5_gr_last_sent_sid_with_cs1": "e41a4e28-a166-4676-80af-53221185ba9d",
    "aba0d864c66383b5_gr_session_id_sent_vst": "e41a4e28-a166-4676-80af-53221185ba9d",
    "Hm_lpvt_5023f5fc98cfb5712c364bb50b12e50e": "1726728543",
    "mp_ec424f4c03f8701f7226f5a009d90586_mixpanel": "%7B%22distinct_id%22%3A%20%22%24device%3A191b5dd3c5f6353-09bd6bd13e515b-26001151-1fa400-191b5dd3c5f6353%22%2C%22%24device_id%22%3A%20%22191b5dd3c5f6353-09bd6bd13e515b-26001151-1fa400-191b5dd3c5f6353%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Flogin.koolearn.com%2Fsso%2FtoLogin.do%3Fnext_page%3Dhttps%253A%252F%252Fstudy.koolearn.com%252Fmy%22%2C%22%24initial_referring_domain%22%3A%20%22login.koolearn.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Flogin.koolearn.com%2Fsso%2FtoLogin.do%3Fnext_page%3Dhttps%253A%252F%252Fstudy.koolearn.com%252Fmy%22%2C%22%24initial_referring_domain%22%3A%20%22login.koolearn.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D",
    "kaoyan-0-19833221": "1",
    "kaoyan-0--1": "0",
    "aba0d864c66383b5_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "daxue-ui-pc-exam": "c4154af0b9cf73b22a56061d3597c648",
    "koo-daxue-tiku-exam-webapp": "c050c3b44d723881d36d59d28839ff78",
    "JSESSIONID": "A322D584CB78B28458048686F035CC04"
}
url = "https://exam.koolearn.com/api/exam-process/v1/answer-sheet/226325773955074"

session = requests.session()
response = session.get(url, headers=headers, cookies=cookies)

file_path="C:\\Users\\xiaoj\\Documents\\资料\\xdf"
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

