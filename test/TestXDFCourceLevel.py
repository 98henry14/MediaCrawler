import json

import requests,os
from datetime import datetime
import platform
import traceback
from xdfTest.TestPaper import XDFPaper
from urllib.parse import urlparse, parse_qs
import hmac
import hashlib
# python 连接 redis
import redis

r = redis.Redis(host='localhost', port=6379, db=0)





headers = {
    "accept": "*/*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": "https://study.koolearn.com/fer/subject-change-agreement",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
cookies = {
    "gr_user_id": "180344aa-0c5b-47de-baf4-c5d6ed529441",
    "MEIQIA_TRACK_ID": "2YANdBOEanSI4CQExSj521lvUlW",
    "MEIQIA_VISIT_ID": "2YANdDjTCWbO3v0KFzaOS5OYY7G",
    "pt_1783e324": "uid=j1K-9XsiTid3maJgpa4icw&nid=1&vid=-GsUeZ5pqcaD5CcwLoRyqA&vn=1&pvn=1&sact=1699964532997&to_flag=0&pl=gjhLyBSjw/HoAfMfeNNUsg*pt*1699964512221",
    "__jsluid_s": "30e5337ee8c137c2e671662623ba817b",
    "pt_6dc02627": "uid=EnrqXUQe7KYZHIwbgpu1kA&nid=0&vid=Qa9YjXydaEuuiicdACZZ9w&vn=4&pvn=1&sact=1709729416327&to_flag=1&pl=qo36Ue6jIhjoaZD2gbwyxg*pt*1709729062821",
    "br-client-id": "222f571c-8aee-4f2e-bfb9-9e7417db6fa9",
    "9dee9d3e36a527e1_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "kaoyan-0-18804357": "1",
    "kaoyan-0--1": "0",
    "br-client": "90daac62-cae7-422d-89ab-cd662d056ad8",
    "_ga_8RBHSP5JM6": "GS1.2.1716702843.2.0.1716702843.60.0.0",
    "_ga_VE7D9QXBBY": "GS1.2.1716702844.2.0.1716702844.60.0.0",
    "aba0d864c66383b5_gr_last_sent_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "sharks-webapp-study-common-nginx": "c61a5f7aecd804cd2dae9920d6baf7fc",
    "koo.line": "study",
    "sharks-webapp-studyguonei-nginx": "b548d178bf281b276c46dea9e1a3bd1d",
    "koo-shark-studytools-webapp": "6751e3d410e2e861e5be97079fbb8409",
    "koo-shark-live-webapp": "2d77813fe9f76ba9182145b95393c9f2",
    "sharks-ui-study": "4ff403a0b8807607c75d3440c2c6c12b",
    "Hm_lvt_5023f5fc98cfb5712c364bb50b12e50e": "1726661943",
    "HMACCOUNT": "937221BF9BC51C4E",
    "Hm_lpvt_5023f5fc98cfb5712c364bb50b12e50e": "1726661948",
    "mp_ec424f4c03f8701f7226f5a009d90586_mixpanel": "%7B%22distinct_id%22%3A%20%22%24device%3A18e2311e38db57-03b2366ba66a9f-1d525637-1d73c0-18e2311e38db57%22%2C%22%24device_id%22%3A%20%2218e2311e38db57-03b2366ba66a9f-1d525637-1d73c0-18e2311e38db57%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fstudy.koolearn.com%2Fky%2Flearning%2F188924%2F22666338%2F18800053%22%2C%22%24initial_referring_domain%22%3A%20%22study.koolearn.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Fstudy.koolearn.com%2Fky%2Flearning%2F188924%2F22666338%2F18800053%22%2C%22%24initial_referring_domain%22%3A%20%22study.koolearn.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D",
    "sso.ssoId": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "ssoSessionID": "A90EAE598B71676046A970A3A4F1BC0C-n2",
    "login_token": "login_token_v2_A90EAE598B71676046A970A3A4F1BC0C-n2",
    "_ga": "GA1.1.914741991.1709728842",
    "kaoyan-0-19929592": "1",
    "kaoyan-0-19929590": "0",
    "kaoyan-0-19833221": "1",
    "kaoyan-0-19833222": "0",
    "sharks-webapp-study": "0250E9B420BDB34EBF2527403DDF9BCF",
    "aba0d864c66383b5_gr_session_id": "220179b6-87dc-410b-b48e-e3725f71ee07",
    "aba0d864c66383b5_gr_last_sent_sid_with_cs1": "220179b6-87dc-410b-b48e-e3725f71ee07",
    "9dee9d3e36a527e1_gr_session_id": "700af16f-8e20-4f14-9a89-2930b49d2a09",
    "sharks-webapp-studyguonei": "F7472F7DED47386D702C17586B6B01D1",
    "JSESSIONID": "86117886EAE8FEB49795D34357B15999",
    "9dee9d3e36a527e1_gr_last_sent_sid_with_cs1": "700af16f-8e20-4f14-9a89-2930b49d2a09",
    "9dee9d3e36a527e1_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "Qs_lvt_143225": "1725883186%2C1726316242%2C1726658900%2C1726745113%2C1726930534",
    "Qs_pv_143225": "385773966642047300%2C3950772463349535000%2C4120952658961817000%2C991578409823529300%2C2678822756839445000",
    "aba0d864c66383b5_gr_cs1": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
    "_ga_MYF8GNFSSR": "GS1.1.1726928892.34.1.1726930541.0.0.0"
}

# 189526 = 课程id,  189526:数学,188924:英语,
# 30427213929 = 订单号，固定的
#  pathid路径可取～ 这里是英语二的

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
10: 直播课程
"""

if platform.system() == "Windows":
    file_path = "C:\\Users\\xiaoj\\baidusync\\xdf\\math\\数学2\\"
elif platform.system() == "Darwin":
    file_path = "/Volumes/SandiskSSD/xdf/math/数学2"

if not os.path.exists(file_path):
    os.mkdir(file_path)

session = requests.session()
paper = XDFPaper(file_path, session, headers, cookies)

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
    r1 = session.get(url, headers=headers, cookies=cookies, params=params)
    if r1.status_code == 200:
        d1 = r1.json().get("data")
        cw1 = r1.json().get("cw")
        rvideoId = d1.get("roomboxInfo").get("rvideoId")
        otherInfo['rvideoId'] = rvideoId
        r.hset(f"xdf:video:pathid_{pathId}", rvideoId,json.dumps(otherInfo,ensure_ascii=False ) )
        # rheaderJson = d1.get("roomboxInfo").get("rheaderJson")
        # # 签名需要重新加密
        # headers.update(json.loads(rheaderJson))
        # m3u8url = "https://media-vod.roombox.xdf.cn/v1/play/getVideoUrl"
        # data = {
        #     "definition": "SD,LD,FD,HD,2K,4K,OD,SQ,HQ,AUTO",
        #     "enc_type": 0,
        #     "stream_type": "",
        #     "url_type": 0,
        #     "video_id": rvideoId,
        #     "exclude_enc_type": [
        #         0
        #     ]
        # }
        # d2 = requests.post(m3u8url,headers=headers, cookies=cookies, data=data)
        # if d2.status_code == 200:
        #     urlinfo = d2.json().get("url_infos")
        #     if urlinfo[0].get("url"):
        #         r2 = requests.get(urlinfo[0].get("url"), headers=headers, cookies=cookies)
        #         with open(os.path.join(otherInfo.get("pathName"), otherInfo.get("name")+".m3u8"), "w") as f:
        #             f.write(r2.content)
        #     # for m3u in urlinfo:
        # else:
        #     print("get m3u8 url fail", d2.json())
    else:
        print("查询课程信息出错了....",r1.json())
def recursion_req(rurl,rparams,map):
    response = session.get(rurl, headers=headers, cookies=cookies, params=rparams)
    if response.status_code == 200:
        print(response.json())
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
                    if not final or (final and item.get("type") in [0,1]):
                        map.get("pathName").append(item.get("name"))


                if not os.path.exists(os.path.join(file_path, os.path.sep.join(map.get("pathName")))) :
                    print("创建文件夹")
                    os.mkdir(os.path.join(file_path,os.path.sep.join(map.get("pathName"))))

                if final:
                    if item.get("type") == 0 and not item.get("id") and not item.get("groupId"):
                    #     这里可能是可选的内容，要重新处理下
                        groupMap = {t.get('id'): t.get("name") for t in item.get('groups')}
                        nodeList = item.get("nodeId").split(",")
                        le = item.get("level") + 1 if item.get("level") else "2"
                        for n in nodeList:
                            map.get("path").append(n)
                            map.get("pathName").append(groupMap.get(n))
                            newParams = {
                                "pathId": map["path"][0],
                                "nodeId": n,
                                "level": le,
                                "_": int(datetime.now().timestamp()) * 1000
                            }

                            newParams["learningSubjectId"] = map["path"][1]

                            recursion_req(url, newParams, map)
                            map.get("path").pop()
                            map.get("pathName").pop()
                        map.get("pathName").pop()

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
                        if not r.exists(f"xdf:video:check_pathid_{pathId}:{item.get('id')}"):
                            get_video_url(course,node,info)
                            r.set(f"xdf:video:check_pathid_{pathId}:{item.get('id')}",info.get('rvideoId'))
                    if item.get("type") == 1:
                        map.get("pathName").pop()

                    if item.get("type") == 3 :
                        item.get('jumpUrl')
                        resp = requests.get(f"https://study.koolearn.com{item.get('jumpUrl')}",headers=headers,cookies=cookies)
                        if resp.status_code == 200:
                            up = urlparse(resp.request.url)
                            params = parse_qs(up.query)
                            if params.get('testResultId'):
                                print("试卷url",resp.request.url)
                                testResultId = params['testResultId'][0]
                                paper.run(examId=testResultId,file_path=os.path.join(file_path,os.path.sep.join(map.get("pathName"))))
                            else:
                                # 如果没点击过的试卷无法按照上面的方式处理 todo
                                if up.path.endswith("start-exam"):
                                    paramsmap = {key: value[0] for key, value in params.items()}
                                    detail_url = f"https://exam.koolearn.com/api/paper/v1/detail?paperVersion=&paperId={paramsmap.get('paperId')}"
                                    r1 = session.get(detail_url)

                                    if r1.status_code == 200 and r1.json().get('status')==0:
                                        version =  r1.json().get('data').get('paperVersion')
                                        paramsmap.update({'paperVersion':version})
                                        start_url = "https://exam.koolearn.com/api/exam-process/v1/start"
                                        r2=requests.post(start_url,headers=headers,cookies=cookies,json=paramsmap)
                                        if r2.status_code == 200 and r2.json().get('status')==0:
                                            paper.run(examId=r2.json().get('data').get('testResultId'),file_path=os.path.join(file_path,os.path.sep.join(map.get("pathName"))))
                                        else:
                                            print("开启试卷出错了。",r2.json())
                                    else:
                                        print("请求试卷详情出错了...",r1.text())

                                print("没有找到试卷的id,",resp.request.url)
                        else:
                            print("请求试卷出错了",resp.status_code)

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
try:
    recursion_req(url,params, {})
except Exception as e:
    # e.with_traceback()
    traceback.print_exc()
    print("出错了,",e)
finally:
    if r:
        r.close()


