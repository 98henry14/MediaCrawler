#!/opt/homebrew/Frameworks/Python.framework/Versions/3.9/bin/
# -*- codig:utf-8 -*-
import os,re,json
from concurrent.futures import ThreadPoolExecutor
import requests

class XDFPaper:
    def __init__(self,file_path,session,headers,cookies):
        self.file_path = file_path
        self.session = session
        self.headers = headers
        self.cookies = cookies
        self.imgParttern = re.compile(r'<img.*?src="(.*?)".*?>')
        self.pTagParttern = re.compile(r'<p>(.*?)</p>')

    def downloadImg(self,img):
        qs = img.group(1)
        imgName = qs.split("/")[-1]
        img = self.session.get(qs)
        with open(os.path.join(self.file_path, "img", imgName), 'wb') as file:
            file.write(img.content)
        return f"![]({qs})"

    def replaceImg(self,content):
        return re.sub(self.imgParttern, self.downloadImg, content)

    def fetchContent(self,content):
        notp = re.findall(self.pTagParttern, content)
        if notp:
            new_content = ""
            for np in notp:
                new_content = new_content + "" + self.replaceImg(np)

            return new_content
        else:
            return content

    def getDeatil(self,qs):
        url = "https://exam.koolearn.com/api/question/v1/detail"
        data = {
            "questionId": qs.get("questionId"),
            "questionVersion": "1",
            "queryType": 2
        }
        data = json.dumps(data, separators=(',', ':'))
        h2 = self.headers
        h2.update({"content-type": "application/json", "origin": "https://exam.koolearn.com"})

        response = requests.post(url, headers=h2, cookies=self.cookies, data=data)
        if response.status_code != 200 or response.json().get('status') != 0:
            print("请求失败,", response.json())

        info = response.json().get('data')
        info['questionStem'] = self.fetchContent(info.get('questionStem'))

        return info

    def run(self,examId,file_path=None):
        if file_path:
            self.file_path = file_path
            if not os.path.exists(os.path.join(self.file_path, "img")):
                os.mkdir(os.path.join(self.file_path, "img"))
        url = f"https://exam.koolearn.com/api/exam-process/v1/answer-sheet/{examId}"
        response = self.session.get(url, headers=self.headers, cookies=self.cookies)
        data = response.json().get('data')
        print(response.json())
        write_file_name = os.path.join(self.file_path, f"{data.get('paperName')}.md")
        if os.path.exists(write_file_name):
            return
        content = []
        for mod in data.get('modules'):
            content.append(f"# {mod.get('nodeName')}({mod.get('nodeScore')})")
            index = 0
            for ss in mod.get('structs'):
                content.append(f"## {ss.get('nodeName')}({ss.get('nodeScore')})")
                order = ss.get('nodeOrders')
                qs_list = ss.get("questions")
                qs_map = {item.get('questionId'): item for item in qs_list}
                results = []
                with ThreadPoolExecutor(max_workers=10) as pool:
                    futures = pool.map(self.getDeatil, qs_list)
                    for result in futures:
                        results.append(result)
                new_list = sorted(results, key=lambda x: qs_map.get(x.get("questionId")).get("nodeOrders"))
                for question in new_list:
                    index = index + 1
                    qs = qs_map.get(question.get('questionId'))
                    content.append(f"### {index}.{question.get('bizQuestionName')}({qs.get('nodeScore')})")
                    content.append(f"{self.fetchContent(question.get('questionStem'))}")
                    for op in question.get("options"):
                        for o1 in op:
                            content.append(f"- {o1.get('optionLabel')}.{self.fetchContent(o1.get('optionValue'))}")

                    content.append(f"[^{index}]: {'*' * 100}")
                    content.append(f"**【标准答案】：{question.get('standardAnswer')} **")
                    for ans in question.get("analysis"):
                        for a1 in ans:
                            if a1.get('analysisValue'):
                                content.append(f"{self.fetchContent(a1.get('analysisValue'))}")
                    content.append("***")

        if content:
            with open(write_file_name, 'w', encoding="utf-8") as file:
                file.write("\n".join(content))