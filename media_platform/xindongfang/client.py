import asyncio
import datetime
import json
import re
from typing import Any, Callable, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from playwright.async_api import BrowserContext, Page
from tenacity import retry, stop_after_attempt, wait_fixed

import config
from base.base_crawler import AbstractApiClient
from tools import utils
import base64
import os
from concurrent.futures import ThreadPoolExecutor

from .exception import DataFetchError, IPBlockError
# from .field import SearchNoteType, SearchSortType
# from .help import get_search_id, sign
import requests


class XindongfangClient(AbstractApiClient):
    def __init__(
            self,
            timeout=60,
            proxies=None,
            *,
            headers: Dict[str, str],
            playwright_page: Page,
            cookie_dict: Dict[str, str],
    ):
        self.proxies = proxies
        self.timeout = timeout
        self.headers = headers
        self._host = "https://study.koolearn.com/"
        self._domain = "https://study.koolearn.com/"
        self.IP_ERROR_STR = "网络连接异常，请检查网络设置或重启试试"
        self.IP_ERROR_CODE = 300012
        self.NOTE_ABNORMAL_STR = "笔记状态异常，请稍后查看"
        self.NOTE_ABNORMAL_CODE = -510001
        self.playwright_page = playwright_page
        self.cookie_dict = cookie_dict
        self.imgParttern = re.compile(r'<img.*?src="(.*?)".*?>')
        self.pTagParttern = re.compile(r'<p>(.*?)</p>')

    async def _pre_headers(self, url: str, data=None) -> Dict:
        """
        请求头参数签名
        Args:
            url:
            data:

        Returns:

        """
        # encrypt_params = await self.playwright_page.evaluate("([url, data]) => window._webmsxyw(url,data)", [url, data])
        # local_storage = await self.playwright_page.evaluate("() => window.localStorage")
        # signs = sign(
        #     a1=self.cookie_dict.get("a1", ""),
        #     b1=local_storage.get("b1", ""),
        #     x_s=encrypt_params.get("X-s", ""),
        #     x_t=str(encrypt_params.get("X-t", ""))
        #
        #
        # headers = {
        #     "X-S": signs["x-s"],
        #     "X-T": signs["x-t"],
        #     "x-S-Common": signs["x-s-common"],
        #     "X-B3-Traceid": signs["x-b3-traceid"]
        # }
        # self.headers.update(headers)
        return self.headers

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def request(self, method, url, **kwargs) -> Union[str, Any]:
        """
        封装httpx的公共请求方法，对请求响应做一些处理
        Args:
            method: 请求方法
            url: 请求的URL
            **kwargs: 其他请求参数，例如请求头、请求体等

        Returns:

        """
        # return response.text
        return_response = kwargs.pop('return_response', False)

        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.request(
                method, url, timeout=self.timeout,
                **kwargs
            )

        if return_response:
            return response.text
        data: Dict = response.json()
        if data.get('status') == 0:
            return data.get("data", data.get("message", {}))
        elif data.get('status') == self.IP_ERROR_CODE:
            raise IPBlockError(self.IP_ERROR_STR)
        else:
            raise DataFetchError(data.get("msg", None))

    async def get(self, uri: str, params=None) -> Dict:
        """
        GET请求，对请求头签名
        Args:
            uri: 请求路由
            params: 请求参数

        Returns:

        """
        final_uri = uri
        if isinstance(params, dict):
            final_uri = (f"{uri}?"
                         f"{urlencode(params)}")
        headers = await self._pre_headers(final_uri)
        if final_uri.startswith("http"):
            url = final_uri
        else:
            url = f"{self._host}{final_uri}"
        return await self.request(method="GET", url=url, headers=headers)

    async def post(self, uri: str, data: dict, **kwargs) -> Dict:
        """
        POST请求，对请求头签名
        Args:
            uri: 请求路由
            data: 请求体参数

        Returns:

        """
        headers = await self._pre_headers(uri, data)
        json_str = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        if uri.startswith("http"):
            url = uri
        else:
            url = f"{self._host}{uri}"

        return await self.request(method="POST", url=url, data=json_str, headers=headers, **kwargs)
    async def get_decrypt_key(self,url,query_params):
        tk = json.loads(base64.b64decode(query_params['MtsHlsUriToken'][0]))
        # print(tk)
        key = tk['key']
        async with httpx.AsyncClient(proxies=self.proxies) as client:
           async with client.stream("GET", url,headers=self.headers, timeout=self.timeout) as resp:
                newR = []
                # resp.raw.decode_content = True
                # dt = resp.raw.read()
                # for d in dt:
                #     newR.append(d ^ key)
                # async for d in resp.aiter_raw():
                async for dt in resp.aiter_raw():
                    for d in dt:
                        newR.append(d ^ key)
                return bytes(newR)


    async def get_note_media(self, url: str) -> Union[bytes, None]:
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.request("GET", url, timeout=self.timeout)
            if not response.reason_phrase == "OK":
                utils.logger.error(f"[XindongfangClient.get_note_media] request {url} err, res:{response.text}")
                return None
            else:
                return response.content

    async def pong(self) -> bool:
        """
        用于检查登录态是否失效了
        Returns:

        """
        """get a note to check if login state is ok"""
        utils.logger.info("[XindongfangClient.pong] Begin to pong xdf...")
        ping_flag = False
        try:
            note_card: Dict = await self.get_note_by_keyword(keyword="小红书")
            if note_card.get("items"):
                ping_flag = True
        except Exception as e:
            utils.logger.error(f"[XindongfangClient.pong] Ping xhs failed: {e}, and try to login again...")
            ping_flag = False
        return ping_flag

    async def update_cookies(self, browser_context: BrowserContext):
        """
        API客户端提供的更新cookies方法，一般情况下登录成功后会调用此方法
        Args:
            browser_context: 浏览器上下文对象

        Returns:

        """
        cookie_str, cookie_dict = utils.convert_cookies(await browser_context.cookies())
        self.headers["Cookie"] = cookie_str
        self.cookie_dict = cookie_dict

    async def get_note_by_keyword(
            self, keyword: str,
            page: int = 1, page_size: int = 20,
            # sort: SearchSortType = SearchSortType.GENERAL,
            # note_type: SearchNoteType = SearchNoteType.ALL
    ) -> Dict:
        """
        根据关键词搜索笔记
        Args:
            keyword: 关键词参数
            page: 分页第几页
            page_size: 分页数据长度
            sort: 搜索结果排序指定
            note_type: 搜索的笔记类型

        Returns:

        """
        uri = f"/common/find/user?_={int(datetime.datetime.now().timestamp())*1000}"

        return await self.get(uri)

    async def get_note_by_id(self, note_id: str, xsec_source: str, xsec_token: str) -> Dict:
        """
        获取笔记详情API
        Args:
            note_id:笔记ID
            xsec_source: 渠道来源
            xsec_token: 搜索关键字之后返回的比较列表中返回的token

        Returns:

        """
        if xsec_source == "":
            xsec_source = "pc_search"

        data = {
            "source_note_id": note_id,
            "image_formats": ["jpg", "webp", "avif"],
            "extra": {"need_body_topic": 1},
            "xsec_source": xsec_source,
            "xsec_token": xsec_token
        }
        uri = "/api/sns/web/v1/feed"
        res = await self.post(uri, data)
        if res and res.get("items"):
            res_dict: Dict = res["items"][0]["note_card"]
            return res_dict
        # 爬取频繁了可能会出现有的笔记能有结果有的没有
        utils.logger.error(f"[XindongfangClient.get_note_by_id] get note id:{note_id} empty and res:{res}")
        return dict()

    async def get_note_comments(self, note_id: str, cursor: str = "") -> Dict:
        """
        获取一级评论的API
        Args:
            note_id: 笔记ID
            cursor: 分页游标

        Returns:

        """
        uri = "/api/sns/web/v2/comment/page"
        params = {
            "note_id": note_id,
            "cursor": cursor,
            "top_comment_id": "",
            "image_formats": "jpg,webp,avif"
        }
        return await self.get(uri, params)

    async def get_note_sub_comments(self, note_id: str, root_comment_id: str, num: int = 10, cursor: str = ""):
        """
        获取指定父评论下的子评论的API
        Args:
            note_id: 子评论的帖子ID
            root_comment_id: 根评论ID
            num: 分页数量
            cursor: 分页游标

        Returns:

        """
        uri = "/api/sns/web/v2/comment/sub/page"
        params = {
            "note_id": note_id,
            "root_comment_id": root_comment_id,
            "num": num,
            "cursor": cursor,
        }
        return await self.get(uri, params)

    async def get_note_all_comments(self, note_id: str, crawl_interval: float = 1.0,
                                    callback: Optional[Callable] = None) -> List[Dict]:
        """
        获取指定笔记下的所有一级评论，该方法会一直查找一个帖子下的所有评论信息
        Args:
            note_id: 笔记ID
            crawl_interval: 爬取一次笔记的延迟单位（秒）
            callback: 一次笔记爬取结束后

        Returns:

        """
        result = []
        comments_has_more = True
        comments_cursor = ""
        while comments_has_more:
            comments_res = await self.get_note_comments(note_id, comments_cursor)
            comments_has_more = comments_res.get("has_more", False)
            comments_cursor = comments_res.get("cursor", "")
            if "comments" not in comments_res:
                utils.logger.info(
                    f"[XindongfangClient.get_note_all_comments] No 'comments' key found in response: {comments_res}")
                break
            comments = comments_res["comments"]
            if callback:
                await callback(note_id, comments)
            await asyncio.sleep(crawl_interval)
            result.extend(comments)
            sub_comments = await self.get_comments_all_sub_comments(comments, crawl_interval, callback)
            result.extend(sub_comments)
        return result

    async def get_comments_all_sub_comments(self, comments: List[Dict], crawl_interval: float = 1.0,
                                            callback: Optional[Callable] = None) -> List[Dict]:
        """
        获取指定一级评论下的所有二级评论, 该方法会一直查找一级评论下的所有二级评论信息
        Args:
            comments: 评论列表
            crawl_interval: 爬取一次评论的延迟单位（秒）
            callback: 一次评论爬取结束后

        Returns:
        
        """
        if not config.ENABLE_GET_SUB_COMMENTS:
            utils.logger.info(
                f"[XiaoHongShuCrawler.get_comments_all_sub_comments] Crawling sub_comment mode is not enabled")
            return []

        result = []
        for comment in comments:
            note_id = comment.get("note_id")
            sub_comments = comment.get("sub_comments")
            if sub_comments and callback:
                await callback(note_id, sub_comments)

            sub_comment_has_more = comment.get("sub_comment_has_more")
            if not sub_comment_has_more:
                continue

            root_comment_id = comment.get("id")
            sub_comment_cursor = comment.get("sub_comment_cursor")

            while sub_comment_has_more:
                comments_res = await self.get_note_sub_comments(note_id, root_comment_id, 10, sub_comment_cursor)
                sub_comment_has_more = comments_res.get("has_more", False)
                sub_comment_cursor = comments_res.get("cursor", "")
                if "comments" not in comments_res:
                    utils.logger.info(
                        f"[XindongfangClient.get_comments_all_sub_comments] No 'comments' key found in response: {comments_res}")
                    break
                comments = comments_res["comments"]
                if callback:
                    await callback(note_id, comments)
                await asyncio.sleep(crawl_interval)
                result.extend(comments)
        return result

    async def get_creator_info(self, user_id: str) -> Dict:
        """
        通过解析网页版的用户主页HTML，获取用户个人简要信息
        PC端用户主页的网页存在window.__INITIAL_STATE__这个变量上的，解析它即可
        eg: https://www.xiaohongshu.com/user/profile/59d8cb33de5fb4696bf17217
        """
        uri = f"/user/profile/{user_id}"
        html_content = await self.request("GET", self._domain + uri, return_response=True, headers=self.headers)
        match = re.search(r'<script>window.__INITIAL_STATE__=(.+)<\/script>', html_content, re.M)

        if match is None:
            return {}

        info = json.loads(match.group(1).replace(':undefined', ':null'), strict=False)
        if info is None:
            return {}
        return info.get('user').get('userPageData')

    async def get_notes_by_creator(
            self, creator: str,
            cursor: str,
            page_size: int = 30
    ) -> Dict:
        """
        获取博主的笔记
        Args:
            creator: 博主ID
            cursor: 上一页最后一条笔记的ID
            page_size: 分页数据长度

        Returns:

        """
        uri = "/api/sns/web/v1/user_posted"
        data = {
            "user_id": creator,
            "cursor": cursor,
            "num": page_size,
            "image_formats": "jpg,webp,avif"
        }
        return await self.get(uri, data)

    async def get_all_notes_by_creator(self, user_id: str, crawl_interval: float = 1.0,
                                       callback: Optional[Callable] = None) -> List[Dict]:
        """
        获取指定用户下的所有发过的帖子，该方法会一直查找一个用户下的所有帖子信息
        Args:
            user_id: 用户ID
            crawl_interval: 爬取一次的延迟单位（秒）
            callback: 一次分页爬取结束后的更新回调函数

        Returns:

        """
        result = []
        notes_has_more = True
        notes_cursor = ""
        while notes_has_more:
            notes_res = await self.get_notes_by_creator(user_id, notes_cursor)
            if not notes_res:
                utils.logger.error(
                    f"[XindongfangClient.get_notes_by_creator] The current creator may have been banned by xhs, so they cannot access the data.")
                break

            notes_has_more = notes_res.get("has_more", False)
            notes_cursor = notes_res.get("cursor", "")
            if "notes" not in notes_res:
                utils.logger.info(
                    f"[XindongfangClient.get_all_notes_by_creator] No 'notes' key found in response: {notes_res}")
                break

            notes = notes_res["notes"]
            utils.logger.info(
                f"[XindongfangClient.get_all_notes_by_creator] got user_id:{user_id} notes len : {len(notes)}")
            if callback:
                await callback(notes)
            await asyncio.sleep(crawl_interval)
            result.extend(notes)
        return result

    async def get_note_short_url(self, note_id: str) -> Dict:
        """
        获取笔记的短链接
        Args:
            note_id: 笔记ID

        Returns:

        """
        uri = f"/api/sns/web/short_url"
        data = {
            "original_url": f"{self._domain}/discovery/item/{note_id}"
        }
        return await self.post(uri, data=data, return_response=True)

    async def get_note_by_id_from_html(self, note_id: str):
        """
        通过解析网页版的笔记详情页HTML，获取笔记详情
        copy from https://github.com/ReaJason/xhs/blob/eb1c5a0213f6fbb592f0a2897ee552847c69ea2d/xhs/core.py#L217-L259
        thanks for ReaJason
        Args:
            note_id:

        Returns:

        """
        def camel_to_underscore(key):
            return re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower()

        def transform_json_keys(json_data):
            data_dict = json.loads(json_data)
            dict_new = {}
            for key, value in data_dict.items():
                new_key = camel_to_underscore(key)
                if not value:
                    dict_new[new_key] = value
                elif isinstance(value, dict):
                    dict_new[new_key] = transform_json_keys(json.dumps(value))
                elif isinstance(value, list):
                    dict_new[new_key] = [
                        transform_json_keys(json.dumps(item))
                        if (item and isinstance(item, dict))
                        else item
                        for item in value
                    ]
                else:
                    dict_new[new_key] = value
            return dict_new

        url = "https://www.xiaohongshu.com/explore/" + note_id
        html = await self.request(method="GET", url=url, return_response=True, headers=self.headers)
        state = re.findall(r"window.__INITIAL_STATE__=({.*})</script>", html)[0].replace("undefined", '""')
        if state != "{}":
            note_dict = transform_json_keys(state)
            return note_dict["note"]["note_detail_map"][note_id]["note"]
        raise DataFetchError(html)

    async def get_native(self, url: str):
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            return await client.request("GET", url,headers=self.headers, timeout=self.timeout)

    async def get_document(self, url: str):
        hd = self.headers
        if hd.get("Content-Type"):
            hd.pop("Content-Type")
        if hd.get("Referer"):
            hd.pop("Referer")
        hd.update({ "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",})
        async with httpx.AsyncClient(follow_redirects=True,proxies=self.proxies) as client:
            return await client.request("GET", url,headers=hd, timeout=self.timeout,follow_redirects=True)


    async def downloadImg(self,img):
        qs = img.group(1)
        imgName = qs.split("/")[-1]
        img = self.get_native(qs)
        with open(os.path.join(self.file_path, "img", imgName), 'wb') as file:
            file.write(img.content)
        return f"![]({qs})"

    async def replaceImg(self,content):
        return re.sub(self.imgParttern, self.downloadImg, content)

    async def fetchContent(self,content):
        notp = re.findall(self.pTagParttern, content)
        if notp:
            new_content = ""
            for np in notp:
                new_content = new_content + "" + self.replaceImg(np)

            return new_content
        else:
            return content

    async def getDeatil(self,qs):
        url = "https://exam.koolearn.com/api/question/v1/detail"
        data = {
            "questionId": qs.get("questionId"),
            "questionVersion": "1",
            "queryType": 2
        }
        # data = json.dumps(data, separators=(',', ':'))
        h2 = self.headers
        h2.update({"content-type": "application/json", "origin": "https://exam.koolearn.com"})

        info = await self.post(url, data=data)
        # if response.status_code != 200 or response.json().get('status') != 0:
        #     print("请求失败,", response.json())
        #
        # info = response.json().get('data')
        info['questionStem'] = self.fetchContent(info.get('questionStem'))

        return info

    async def run(self,examId,file_path=None):
        if file_path:
            self.file_path = file_path
            if not os.path.exists(os.path.join(self.file_path, "img")):
                os.mkdir(os.path.join(self.file_path, "img"))
        url = f"https://exam.koolearn.com/api/exam-process/v1/answer-sheet/{examId}"
        data = await self.get(url)
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
                # results = []

                # with ThreadPoolExecutor(max_workers=10) as pool:
                #     futures = pool.map(self.getDeatil, qs_list)
                #     for result in futures:
                #         results.append(result)

                exec = ThreadPoolExecutor(max_workers=10)
                loop = asyncio.get_event_loop()
                task = [loop.run_in_executor(exec, asyncio.run, self.getDeatil(qs)) for qs in qs_list]
                results = await asyncio.gather(*task)
                new_list = sorted(results, key=lambda x: qs_map.get(x.get("questionId")).get("nodeOrders"))
                for question in new_list:
                    index = index + 1
                    qs = qs_map.get(question.get('questionId'))
                    content.append(f"### {index}.{question.get('bizQuestionName')}({qs.get('nodeScore')})")
                    content.append(f"{await self.fetchContent(question.get('questionStem'))}")
                    for op in question.get("options"):
                        for o1 in op:
                            content.append(f"- {o1.get('optionLabel')}.{await self.fetchContent(o1.get('optionValue'))}")

                    content.append(f"[^{index}]: {'*' * 100}")
                    content.append(f"**【标准答案】：{question.get('standardAnswer')} **")
                    for ans in question.get("analysis"):
                        for a1 in ans:
                            if a1.get('analysisValue'):
                                content.append(f"{await self.fetchContent(a1.get('analysisValue'))}")
                    content.append("***")

        if content:
            with open(write_file_name, 'w', encoding="utf-8") as file:
                file.write("\n".join(content))

