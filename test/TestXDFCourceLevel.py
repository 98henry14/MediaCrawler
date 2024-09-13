import json

import requests,os
from datetime import datetime

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://study.koolearn.com/ky/course/189526/30427213929",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
cookies = {
    "__jsluid_s": "f3518d5def40528f4af482f8671dfff3",
    "gr_user_id": "ccb32893-c33e-44d3-bf15-de1537360181",
    "aba0d864c66383b5_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "Qs_lvt_143225": "1725696856",
    "9dee9d3e36a527e1_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "koo.line": "study",
    "sharks-webapp-studyguonei-nginx": "58ff8b11240b83e6e6ff87bb369b7e74",
    "easeMobId": "koolearn1725712051456838882",
    "easeMobPassword": "koolearn1725712051456838882",
    "MEIQIA_TRACK_ID": "2lk77SJE9RG8hKuAacDrqVEVqZA",
    "MEIQIA_VISIT_ID": "2lk77SeWZjOACKj4nxhNC30VZN8",
    "Qs_pv_143225": "2416550789484732400%2C2619313347871156000%2C1671800531537438000%2C1672103693951368400",
    "koo-shark-studytools-webapp": "a7c4737439ebb338a69597a9ab55bfcf",
    "sharks-webapp-study-common-nginx": "445ae649f905a552d5e0c772aad178d2",
    "sso.ssoId": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "ssoSessionID": "B788773480B41A10287D41A5FAB031A8-n2",
    "login_token": "login_token_v2_B788773480B41A10287D41A5FAB031A8-n2",
    "Hm_lvt_5023f5fc98cfb5712c364bb50b12e50e": "1725332527,1726036134",
    "HMACCOUNT": "34DEDCD166447D6D",
    "sharks-ui-study": "7cace576b2bdfa21fda3fdd800d3aea4",
    "_ga": "GA1.1.993296956.1713625335",
    "9dee9d3e36a527e1_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "_ga_MYF8GNFSSR": "GS1.1.1726104294.6.0.1726104294.0.0.0",
    "sharks-webapp-study": "5ED8EB88D37782D91B245B52BBECE926",
    "aba0d864c66383b5_gr_session_id": "1622e709-9e97-4ae6-b65d-3998d33c7917",
    "aba0d864c66383b5_gr_last_sent_sid_with_cs1": "1622e709-9e97-4ae6-b65d-3998d33c7917",
    "aba0d864c66383b5_gr_session_id_sent_vst": "1622e709-9e97-4ae6-b65d-3998d33c7917",
    "sharks-webapp-studyguonei": "82102372BA5B8DD93AE528FD9404B9E7",
    "JSESSIONID": "DC299369C1999E7B6D5CD95AA5AAED3F",
    "aba0d864c66383b5_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "Hm_lpvt_5023f5fc98cfb5712c364bb50b12e50e": "1726215112",
    "mp_ec424f4c03f8701f7226f5a009d90586_mixpanel": "%7B%22distinct_id%22%3A%20%22%24device%3A191b5dd3c5f6353-09bd6bd13e515b-26001151-1fa400-191b5dd3c5f6353%22%2C%22%24device_id%22%3A%20%22191b5dd3c5f6353-09bd6bd13e515b-26001151-1fa400-191b5dd3c5f6353%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Flogin.koolearn.com%2Fsso%2FtoLogin.do%3Fnext_page%3Dhttps%253A%252F%252Fstudy.koolearn.com%252Fmy%22%2C%22%24initial_referring_domain%22%3A%20%22login.koolearn.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Flogin.koolearn.com%2Fsso%2FtoLogin.do%3Fnext_page%3Dhttps%253A%252F%252Fstudy.koolearn.com%252Fmy%22%2C%22%24initial_referring_domain%22%3A%20%22login.koolearn.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D"
}

# 189526 = 课程id,  189526:数学,188924:英语,
# 30427213929 = 订单号
productId = "189526"
pathId = "344056"
url = f"https://study.koolearn.com/ky/course_kc_data/{productId}/30427213929/1/0"
params = {
    "pathId": pathId,
    "nodeId": "-1",
    "level": "1",
    "_": int(datetime.now().timestamp())*1000
}
"""
type类型的可能取值,只针对当前查询目录的接口
1: 文件夹？
2：视频？
3：文档测试
8：截图文档？
"""


file_path = "C:\\Users\\xiaoj\\baidusync\\xdf\\math\\数学2"

if not os.path.exists(file_path):
    os.mkdir(file_path)

def get_video_url(courseId,nodeId,otherInfo):
    url = "https://study.koolearn.com/common/learning/getNewVideoInfo"
    params = {
        "courseId": courseId, #"22666340",
        "nodeId": nodeId, #"19056903",
        "urlPart": "ky",
        "productId": productId,
        "subjectId": "0",
        "seasonId": "243",
        "orderNo": "30427213929",
        "_": int(datetime.now().timestamp()) * 1000
    }
    r1 = requests.get(url, headers=headers, cookies=cookies, params=params)
    if r1.status_code == 200:
        d1 = r1.json().get("data")
        cw1 = r1.json().get("cw")
        rvideoId = d1.get("roomboxInfo").get("rvideoId")

        m3u8url = "https://media-vod.roombox.xdf.cn/v1/play/getVideoUrl"
        data = {
            "definition": "SD,LD,FD,HD,2K,4K,OD,SQ,HQ,AUTO",
            "enc_type": 0,
            "stream_type": "",
            "url_type": 0,
            "video_id": rvideoId,
            "exclude_enc_type": [
                0
            ]
        }
        d2 = requests.post(m3u8url,headers=headers, cookies=cookies, data=data)
        if d2.status_code == 200:
            urlinfo = d2.json().get("url_infos")
            if urlinfo[0].get("url"):
                r2 = requests.get(urlinfo[0].get("url"), headers=headers, cookies=cookies)
                with open(os.path.join(otherInfo.get("pathName"), otherInfo.get("name")+".m3u8"), "w") as f:
                    f.write(r2.content)
            # for m3u in urlinfo:
def recursion_req(rurl,rparams,map):
    response = requests.get(rurl, headers=headers, cookies=cookies, params=rparams)
    if response.status_code == 200:
        # print(response.json())
        # print(response)
        data = response.json().get("data")
        if not map.get("path"):
            map["path"] = [rparams.get("pathId")]


        if data:
            for item in data:
                final = item.get("isLeaf") if item.get("isLeaf") else False

                if not map.get("pathName"):
                    map["pathName"] = [item.get("name")]
                else:
                    if not final or (final and item.get("type") == 1):
                        map.get("pathName").append(item.get("name"))


                if not os.path.exists(os.path.join(file_path, os.path.sep.join(map.get("pathName")))) :
                    os.mkdir(os.path.join(file_path,os.path.sep.join(map.get("pathName"))))

                if final:

                    if item.get("type") == 2:
                        # 视频文件 可以获取路径从而拿到m3u8文件
                        jumpUrl = item.get("jumpUrl")
                        ulist = jumpUrl.split("/")
                        product = ulist[3]
                        course = ulist[5]
                        node = ulist[6]
                        info = {'jumpUrl': jumpUrl,
                                'name': item.get("name"),
                                'id': item.get("id"),
                                'nodeId': item.get("nodeId"),
                                'lsVersionId': item.get("lsVersionId"),
                                'videoLength': item.get("videoLength"),
                                'live': item.get("live"),
                                'pathName': os.path.sep.join(map.get("pathName")),
                                }
                        get_video_url(course,node,info)
                    if item.get("type") == 1:
                        map.get("pathName").pop()


                else:
                    map.get("path").append(item.get("nodeId"))
                    newParams = {
                        "pathId": map["path"][0],
                        "nodeId": item.get("nodeId"),
                        "level": item.get("level") + 1 if item.get("level") else "2",
                        "_": int(datetime.now().timestamp()) * 1000
                    }

                    newParams["learningSubjectId"] = map["path"][1]

                    recursion_req(url, newParams, map)
                    map.get("path").pop()
                    map.get("pathName").pop()

    else:
        print("请求失败，状态码：", response.status_code)
        return None

# response = requests.get(url, headers=headers, cookies=cookies, params=params)
recursion_req(url,params, {})


