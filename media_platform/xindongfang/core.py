import asyncio
import os, re, json
import platform
import random
from asyncio import Task
from typing import Dict, List, Optional, Tuple

from playwright.async_api import (BrowserContext, BrowserType, Page,
                                  async_playwright)

import config
from base.base_crawler import AbstractCrawler
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from store import xhs as xhs_store
from tools import utils,time_util
from var import crawler_type_var, source_keyword_var

from .client import XindongfangClient
from .exception import DataFetchError
# from .field import SearchSortType
from .login import XindongfangLogin
from cache.redis_cache import RedisCache
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
from urllib.parse import urlparse, parse_qs
import subprocess
import base64
from Crypto.Cipher import AES
import threading

class XindongfangCrawler(AbstractCrawler):
    context_page: Page
    xdf_client: XindongfangClient
    browser_context: BrowserContext

    def __init__(self) -> None:
        self.index_url = "https://study.koolearn.com/my"
        # self.user_agent = utils.get_user_agent()
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.cache = RedisCache()
        self.root_path = config.XDF_ROOT_PATH
        self.ffmpeg_path = config.FFMPEG_PATH

    async def start(self) -> None:
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            ip_proxy_pool = await create_ip_pool(config.IP_PROXY_POOL_COUNT, enable_validate_ip=True)
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = self.format_proxy_info(ip_proxy_info)

        async with async_playwright() as playwright:
            # Launch a browser context.
            chromium = playwright.chromium
            self.browser_context = await self.launch_browser(
                chromium,
                None,
                self.user_agent,
                headless=config.HEADLESS
            )

            # stealth.min.js is a js script to prevent the website from detecting the crawler.
            await self.browser_context.add_init_script(path="libs/stealth.min.js")
            await self.browser_context.add_init_script(path="libs/15359f6a9bf74d07be6934bdcd11f00a.js")
            # add a cookie attribute webId to avoid the appearance of a sliding captcha on the webpage
            await self.browser_context.add_cookies([{
                'name': "webId",
                'value': "xxx123",  # any value
                'domain': ".xiaohongshu.com",
                'path': "/"
            }])
            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            # Create a client to interact with the xiaohongshu website.
            self.xdf_client = await self.create_xdf_client(httpx_proxy_format)
            if not await self.xdf_client.pong():
                login_obj = XindongfangLogin(
                    login_type=config.LOGIN_TYPE,
                    login_phone="",  # input your phone number
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES
                )
                await login_obj.begin()
                await self.xdf_client.update_cookies(browser_context=self.browser_context)

            crawler_type_var.set(config.CRAWLER_TYPE)
            if config.CRAWLER_TYPE == "search":
                # Search for notes and retrieve their comment information.
                # await self.search()
                await self.handle_all_path()
                await self.test()
            elif config.CRAWLER_TYPE == "detail":
                # Get the information and comments of the specified post
                await self.get_specified_notes()
            elif config.CRAWLER_TYPE == "creator":
                # Get creator's information and their notes and comments
                await self.get_creators_and_notes()
            else:
                pass

            utils.logger.info("[XindongfangCrawler.start] Xhs Crawler finished ...")

    async def search(self) -> None:
        """Search for notes and retrieve their comment information."""
        pass
        # utils.logger.info("[XindongfangCrawler.search] Begin search xiaohongshu keywords")
        # xhs_limit_count = 20  # xhs limit page fixed value
        # if config.CRAWLER_MAX_NOTES_COUNT < xhs_limit_count:
        #     config.CRAWLER_MAX_NOTES_COUNT = xhs_limit_count
        # start_page = config.START_PAGE
        # for keyword in config.KEYWORDS.split(","):
        #     source_keyword_var.set(keyword)
        #     utils.logger.info(f"[XindongfangCrawler.search] Current search keyword: {keyword}")
        #     page = 1
        #     while (page - start_page + 1) * xhs_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
        #         if page < start_page:
        #             utils.logger.info(f"[XindongfangCrawler.search] Skip page {page}")
        #             page += 1
        #             continue
        #
        #         try:
        #             utils.logger.info(f"[XindongfangCrawler.search] search xhs keyword: {keyword}, page: {page}")
        #             note_id_list: List[str] = []
        #             notes_res = await self.xdf_client.get_note_by_keyword(
        #                 keyword=keyword,
        #                 page=page,
        #                 sort=SearchSortType(config.SORT_TYPE) if config.SORT_TYPE != '' else SearchSortType.GENERAL,
        #             )
        #             utils.logger.info(f"[XindongfangCrawler.search] Search notes res:{notes_res}")
        #             if not notes_res or not notes_res.get('has_more', False):
        #                 utils.logger.info("No more content!")
        #                 break
        #             semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        #             task_list = [
        #                 self.get_note_detail_async_task(
        #                     note_id=post_item.get("id"),
        #                     xsec_source=post_item.get("xsec_source"),
        #                     xsec_token=post_item.get("xsec_token"),
        #                     semaphore=semaphore
        #                 )
        #                 for post_item in notes_res.get("items", {})
        #                 if post_item.get('model_type') not in ('rec_query', 'hot_query')
        #             ]
        #             note_details = await asyncio.gather(*task_list)
        #             for note_detail in note_details:
        #                 if note_detail:
        #                     await xhs_store.update_xhs_note(note_detail)
        #                     await self.get_notice_media(note_detail)
        #                     note_id_list.append(note_detail.get("note_id"))
        #             page += 1
        #             utils.logger.info(f"[XindongfangCrawler.search] Note details: {note_details}")
        #             await self.batch_get_note_comments(note_id_list)
        #         except DataFetchError:
        #             utils.logger.error("[XindongfangCrawler.search] Get note detail error")
        #             break

    async def get_creators_and_notes(self) -> None:
        """Get creator's notes and retrieve their comment information."""
        utils.logger.info("[XindongfangCrawler.get_creators_and_notes] Begin get xiaohongshu creators")
        for user_id in config.XHS_CREATOR_ID_LIST:
            # get creator detail info from web html content
            createor_info: Dict = await self.xdf_client.get_creator_info(user_id=user_id)
            if createor_info:
                await xhs_store.save_creator(user_id, creator=createor_info)

            # Get all note information of the creator
            all_notes_list = await self.xdf_client.get_all_notes_by_creator(
                user_id=user_id,
                crawl_interval=random.random(),
                callback=self.fetch_creator_notes_detail
            )

            note_ids = [note_item.get("note_id") for note_item in all_notes_list]
            await self.batch_get_note_comments(note_ids)

    async def fetch_creator_notes_detail(self, note_list: List[Dict]):
        """
        Concurrently obtain the specified post list and save the data
        """
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = [
            self.get_note_detail_async_task(
                note_id=post_item.get("note_id"),
                xsec_source=post_item.get("xsec_source"),
                xsec_token=post_item.get("xsec_token"),
                semaphore=semaphore
            )
            for post_item in note_list
        ]

        note_details = await asyncio.gather(*task_list)
        for note_detail in note_details:
            if note_detail:
                await xhs_store.update_xhs_note(note_detail)

    async def get_specified_notes(self):
        """Get the information and comments of the specified post"""

        async def get_note_detail_from_html_task(note_id: str, semaphore: asyncio.Semaphore) -> Dict:
            async with semaphore:
                try:
                    _note_detail: Dict = await self.xdf_client.get_note_by_id_from_html(note_id)
                    print("------------------------")
                    print(_note_detail)
                    print("------------------------")
                    if not _note_detail:
                        utils.logger.error(
                            f"[XindongfangCrawler.get_note_detail_from_html] Get note detail error, note_id: {note_id}")
                        return {}
                    return _note_detail
                except DataFetchError as ex:
                    utils.logger.error(f"[XindongfangCrawler.get_note_detail_from_html] Get note detail error: {ex}")
                    return {}
                except KeyError as ex:
                    utils.logger.error(
                        f"[XindongfangCrawler.get_note_detail_from_html] have not fund note detail note_id:{note_id}, err: {ex}")
                    return {}

        get_note_detail_task_list = [
            get_note_detail_from_html_task(note_id=note_id, semaphore=asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)) for
            note_id in config.XHS_SPECIFIED_ID_LIST
        ]

        need_get_comment_note_ids = []
        note_details = await asyncio.gather(*get_note_detail_task_list)
        for note_detail in note_details:
            if note_detail:
                need_get_comment_note_ids.append(note_detail.get("note_id"))
                await xhs_store.update_xhs_note(note_detail)
        await self.batch_get_note_comments(need_get_comment_note_ids)

    async def get_note_detail_async_task(self, note_id: str, xsec_source: str, xsec_token: str, semaphore: asyncio.Semaphore) -> \
            Optional[Dict]:
        """Get note detail"""
        async with semaphore:
            try:
                note_detail: Dict = await self.xdf_client.get_note_by_id(note_id, xsec_source, xsec_token)
                if not note_detail:
                    utils.logger.error(
                        f"[XindongfangCrawler.get_note_detail_async_task] Get note detail error, note_id: {note_id}")
                    return None
                note_detail.update({"xsec_token": xsec_token, "xsec_source": xsec_source})
                return note_detail
            except DataFetchError as ex:
                utils.logger.error(f"[XindongfangCrawler.get_note_detail_async_task] Get note detail error: {ex}")
                return None
            except KeyError as ex:
                utils.logger.error(
                    f"[XindongfangCrawler.get_note_detail_async_task] have not fund note detail note_id:{note_id}, err: {ex}")
                return None

    async def batch_get_note_comments(self, note_list: List[str]):
        """Batch get note comments"""
        if not config.ENABLE_GET_COMMENTS:
            utils.logger.info(f"[XindongfangCrawler.batch_get_note_comments] Crawling comment mode is not enabled")
            return

        utils.logger.info(
            f"[XindongfangCrawler.batch_get_note_comments] Begin batch get note comments, note list: {note_list}")
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list: List[Task] = []
        for note_id in note_list:
            task = asyncio.create_task(self.get_comments(note_id, semaphore), name=note_id)
            task_list.append(task)
        await asyncio.gather(*task_list)

    async def get_comments(self, note_id: str, semaphore: asyncio.Semaphore):
        """Get note comments with keyword filtering and quantity limitation"""
        async with semaphore:
            utils.logger.info(f"[XindongfangCrawler.get_comments] Begin get note id comments {note_id}")
            await self.xdf_client.get_note_all_comments(
                note_id=note_id,
                crawl_interval=random.random(),
                callback=xhs_store.batch_update_xhs_note_comments
            )

    @staticmethod
    def format_proxy_info(ip_proxy_info: IpInfoModel) -> Tuple[Optional[Dict], Optional[Dict]]:
        """format proxy info for playwright and httpx"""
        playwright_proxy = {
            "server": f"{ip_proxy_info.protocol}{ip_proxy_info.ip}:{ip_proxy_info.port}",
            "username": ip_proxy_info.user,
            "password": ip_proxy_info.password,
        }
        httpx_proxy = {
            f"{ip_proxy_info.protocol}": f"http://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}"
        }
        return playwright_proxy, httpx_proxy

    async def create_xdf_client(self, httpx_proxy: Optional[str]) -> XindongfangClient:
        """Create xhs client"""
        utils.logger.info("[XindongfangCrawler.create_xhs_client] Begin create xiaohongshu API client ...")
        cookie_str, cookie_dict = utils.convert_cookies(await self.browser_context.cookies())
        xhs_client_obj = XindongfangClient(
            proxies=httpx_proxy,
            headers={
                "User-Agent": self.user_agent,
                "Cookie": cookie_str,
                "Origin": "https://study.koolearn.com/",
                "Referer": "https://study.koolearn.com/",
                "Content-Type": "application/json;charset=UTF-8"
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
        )
        return xhs_client_obj

    async def launch_browser(
            self,
            chromium: BrowserType,
            playwright_proxy: Optional[Dict],
            user_agent: Optional[str],
            headless: bool = True
    ) -> BrowserContext:
        """Launch browser and create browser context"""
        utils.logger.info("[XindongfangCrawler.launch_browser] Begin create browser context ...")
        # 增加本地chrome路径打开好点
        if platform.system() == "Windows":
            executable_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        elif platform.system() == "Linux":
            executable_path = ""
        else:
            executable_path = ""
        if config.SAVE_LOGIN_STATE:
            # feat issue #14
            # we will save login state to avoid login every time
            user_data_dir = os.path.join(os.getcwd(), "browser_data",
                                         config.USER_DATA_DIR % config.PLATFORM)  # type: ignore
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,  # type: ignore
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
                record_video_dir="./record/"
            )
            return browser_context
        else:
            browser = await chromium.launch(executable_path=executable_path,headless=headless, proxy=playwright_proxy)  # type: ignore
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent,
                # record_video_dir="./record/",
            )
            return browser_context

    async def close(self):
        """Close browser context"""
        await self.browser_context.close()
        # if self.cache:
        #     self.cache.close()
        utils.logger.info("[XindongfangCrawler.close] Browser context closed ...")

    async def get_notice_media(self, note_detail: Dict):
        if not config.ENABLE_GET_IMAGES:
            utils.logger.info(f"[XindongfangCrawler.get_notice_media] Crawling image mode is not enabled")
            return
        await self.get_note_images(note_detail)
        await self.get_notice_video(note_detail)

    async def get_note_images(self, note_item: Dict):
        """
        get note images. please use get_notice_media
        :param note_item:
        :return:
        """
        if not config.ENABLE_GET_IMAGES:
            return
        note_id = note_item.get("note_id")
        image_list: List[Dict] = note_item.get("image_list", [])

        for img in image_list:
            if img.get('url_default') != '':
                img.update({'url': img.get('url_default')})

        if not image_list:
            return
        picNum = 0
        for pic in image_list:
            url = pic.get("url")
            if not url:
                continue
            content = await self.xdf_client.get_note_media(url)
            if content is None:
                continue
            extension_file_name = f"{picNum}.jpg"
            picNum += 1
            await xhs_store.update_xhs_note_image(note_id, content, extension_file_name)

    async def get_notice_video(self, note_item: Dict):
        """
        get note images. please use get_notice_media
        :param note_item:
        :return:
        """
        if not config.ENABLE_GET_IMAGES:
            return
        note_id = note_item.get("note_id")

        videos = xhs_store.get_video_url_arr(note_item)

        if not videos:
            return
        videoNum = 0
        for url in videos:
            content = await self.xdf_client.get_note_media(url)
            if content is None:
                continue
            extension_file_name = f"{videoNum}.mp4"
            videoNum += 1
            await xhs_store.update_xhs_note_image(note_id, content, extension_file_name)

    async def test(self):
        await self.context_page.goto("https://study.koolearn.com/ky/learning/188924/22666338/18800049")


        async with self.context_page.expect_response("**/v1/play/getVideoUrl") as resp:
            info = await resp.value
            text = await info.text()
            json = await info.json()
            print("获取response",info)
            print("获取response",text)
            print("获取response",json)
            self.cache.setStr("18800049",json.get('url_infos')[0])

        async with self.context_page.expect_response(re.compile(r'.*\.m3u8.*')) as r2:
            info = await r2.value
            text = await info.text()
            filename = info.request.url.split("?")[0].split("/")[-1]
            with open(os.path.join("C:\\Users\\xiaoj\\Downloads\\m3u8", filename), "w", encoding="utf-8") as f:
                f.write(text)
            self.cache.setStr(filename.split(".")[0],"m3u8_file_done")

    async def getM3u8File(self,url):
        # await self.context_page.goto("https://study.koolearn.com/ky/learning/188924/22666338/18800049")
        nodeId = url.split("/")[-2]
        pathId = url.split("/")[3]
        if not self.cache.exists(f"xdf:video:check_pathid_{pathId}:{nodeId}"):

            await self.context_page.goto(url)

            async with self.context_page.expect_response(re.compile(r'.*\.m3u8.*')) as r2:
                info = await r2.value
                filename = info.request.url.split("?")[0].split("/")[-1]
                text = await info.text()
                utils.logger.info("[XindongfangCrawler.close] 获取m3u8的文件内容 ...",filename)
    #             写入到本地文件,todo,记得替换路径,这里也可以直接拿到相关的信息然后往下传递
    #             async with open(os.path.join(self.file_path,filename),"w",encoding="utf-8") as f:
    #                 f.write(text)
                ts_urls = []
                key_url = ""
                content = []
                for line in text.split("\n"):
                    if line.startswith('#'):
                        if line.startswith('#EXT-X-KEY:'):
                            key_url = line.split(',')[1].strip().replace("URI=", "").replace("\"", "")
                        else:
                            content.append(line)
                        continue
                    content.append(f"{os.path.sep}{line.split('?')[0]}\n")
                    ts_urls.append(line.strip())
                return key_url, ts_urls, content
        else:
            utils.logger.info("[XindongfangCrawler.close] 获取m3u8文件已经存在,直接返回 ...")



    async def handle_all_path(self):
        """
        处理文件目录跟路径
        todo 一个循环搞死吗?
        """

        product = self.cache.hgetall("product:189526")
        product.get('lessonStage').get('344056')
        product = ["189526"]
        for productId in product:
            path = ["344056"]
            for pathId in path:
                url = f"https://study.koolearn.com/ky/course_kc_data/{productId}/30427213929/1/0"
                params = {
                    "pathId": pathId,
                    "nodeId": "-1",
                    "level": "1",
                    "_": time_util.get_current_timestamp()
                }
                # os.path.join(self.root_path, os.path.sep.join(map.get("pathName")))
                self.file_path = os.path.join(self.root_path, "math/数学2")
                if not os.path.exists(self.file_path):
                    os.mkdir(self.file_path)
                await self.recursion_req(url,params,{})

    async def recursion_req(self,rurl,rparams,map):

        response = self.xdf_client.get(rurl, params=rparams)
        if response.status_code == 200:
            data = response.json().get("data")
            if not map.get("path"):
                map["path"] = [rparams.get("pathId")]

            if data:
                for item in data:
                    final = item.get("isLeaf") if item.get("isLeaf") else False

                    if not map.get("pathName"):
                        map["pathName"] = [item.get("name")]
                    else:
                        if not final or (final and item.get("type") in [0, 1]):
                            map.get("pathName").append(item.get("name"))

                    if not os.path.exists(os.path.join(self.file_path, os.path.sep.join(map.get("pathName")))):
                        utils.logger.info("创建文件夹")

                        os.mkdir(os.path.join(self.file_path, os.path.sep.join(map.get("pathName"))))

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
                                    "_": time_util.get_current_timestamp()
                                }

                                newParams["learningSubjectId"] = map["path"][1]

                                await self.recursion_req(rurl, newParams, map)
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
                                    'file_path':self.file_path,
                                    'pathId': map["path"][0],
                                    }
                            if not self.cache.exists(f"xdf:video:check_pathid_{rparams.get('pathId')}:{item.get('id')}"):
                                # get_video_url(course, node, info)
                                kurl, res, content = await self.getM3u8File(f"{self.xdf_client._host}{jumpUrl}")
                                await self.handle_video( kurl, res, content,info)

                                self.cache.set(f"xdf:video:check_pathid_{rparams.get('pathId')}:{item.get('id')}", info.get('rvideoId'))
                        if item.get("type") == 1:
                            map.get("pathName").pop()

                        if item.get("type") == 3:
                            item.get('jumpUrl')
                            resp = await self.xdf_client.get(f"https://study.koolearn.com{item.get('jumpUrl')}")

                            if resp.status_code == 200:
                                up = urlparse(resp.request.url)
                                params = parse_qs(up.query)
                                if params.get('testResultId'):
                                    utils.logger.info("试卷url", resp.request.url)
                                    testResultId = params['testResultId'][0]
                                    await self.xdf_client.run(examId=testResultId,file_path=os.path.join(self.file_path, os.path.sep.join(map.get("pathName"))))

                                else:
                                    # 如果没点击过的试卷无法按照上面的方式处理 todo
                                    if up.path.endswith("start-exam"):
                                        paramsmap = {key: value[0] for key, value in params.items()}
                                        detail_url = f"https://exam.koolearn.com/api/paper/v1/detail?paperVersion=&paperId={paramsmap.get('paperId')}"
                                        r1 = await self.xdf_client.get(detail_url)

                                        if r1.status_code == 200 and r1.json().get('status') == 0:
                                            version = r1.json().get('data').get('paperVersion')
                                            paramsmap.update({'paperVersion': version})
                                            start_url = "https://exam.koolearn.com/api/exam-process/v1/start"
                                            r2 = await self.xdf_client.post(start_url,paramsmap)
                                            if r2.status_code == 200 and r2.json().get('status') == 0:

                                                await self.xdf_client.run(examId=r2.json().get('data').get('testResultId'),
                                                                          file_path=os.path.join(self.file_path,
                                                                                                 os.path.sep.join(
                                                                                                     map.get(
                                                                                                         "pathName"))))
                                            else:
                                                utils.logger.error("开启试卷出错了。", r2.json())
                                        else:
                                            utils.logger.error("请求试卷详情出错了...", r1.text())

                                    utils.logger.error("没有找到试卷的id,", resp.request.url)
                            else:
                                utils.logger.error("请求试卷出错了", resp.status_code)

                    else:
                        map.get("path").append(item.get("nodeId"))
                        newParams = {
                            "pathId": map["path"][0],
                            "nodeId": item.get("nodeId"),
                            "level": item.get("level") + 1 if item.get("level") else "2",
                            "_": time_util.get_current_timestamp()
                        }

                        newParams["learningSubjectId"] = map["path"][1]

                        self.recursion_req(rurl, newParams, map)
                        map.get("path").pop()
                        map.get("pathName").pop()

        else:

            utils.logger.error("请求失败，状态码：", response.status_code)
            return None

#     todo 1.搬运下载视频的代码
    async def run_azure_command(command):
        try:
            result = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")
            return None

    def generate_new_m3u8_file(self,final_path, new_index_name, content):
        new_m3u8_path = os.path.join(final_path, new_index_name)
        with open(new_m3u8_path, "w") as newfile:
            if content:
                for line in content:
                    if not line.startswith("#"):
                        line = f"{final_path}{line}"
                    newfile.write(line)

    async def decrypt_key(self,raw_content, token):

        tk = json.loads(base64.b64decode(token))
        # print(tk)
        key = tk['key']
        newR = []
        for d in raw_content:
            newR.append(d ^ key)
        return bytes(newR)

    async def handle_video(self, kurl: str, res: str, content: str, map) -> bool:
        # 解析key的 URL
        parsed_url = urlparse(kurl)
        pathId = map.get('pathId')
        file_path = map.get('file_path')

        # 提取查询参数
        query_params = parse_qs(parsed_url.query)
        vid = query_params['vid'][0]

        # 从 redis 获取匹配数据
        info = self.cache.hget(f"xdf:video:pathid_{pathId}", vid)
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

                await self.generate_new_m3u8_file(final_path, new_idx_m3u8_name, content)

                # 提取key，并获取最终解密的key
                kb = await self.xdf_client.get_decrypt_key(kurl,query_params)
                # resp = requests.get(kurl, headers=headers, stream=True)
                # resp.raw.decode_content = True
                # dt = resp.raw.read()
                # kb = self.decrypt_key(dt, query_params['MtsHlsUriToken'][0])
                # print(kb)
                ib = bytes([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

                start = time_util.get_current_time()
                task = []
                print("使用多线程方式下载ts文件")
                with ThreadPoolExecutor(max_workers=20) as executor:
                    # results = executor.map(download_ts,res)
                    task.extend(
                        [executor.submit(self.download_ts, ts_name=ts, vid=vid, kb=kb, ib=ib, final_path=final_path) for ts in res])
                    print("任务总数", len(task))

                as_completed(task, timeout=10)

                ts_file_list = [t.result() for t in task]
                if any(ts in [None] for ts in ts_file_list):
                    print("存在文件下载失败，无法合并")
                    return

                print(f"使用多线程方式下载ts文件完成,文件内容列表为{ts_file_list}\n耗时:{time_util.get_current_time() - start}")
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
                r2 = await self.run_azure_command(f"cd '{final_path}' && {self.ffmpeg_path} -i '{local_m3u8}' -c copy '{merge_mp4_name}' -y")
                del_file_list = "' '".join(ts_file_list)
                r3 = await self.run_azure_command(f"cd '{final_path}' && rm -rf '{del_file_list}' ")
                # print(r3)
                info['generate_mp4_address'] = merge_mp4_name
                # 当前这种方式没有下载到本地无法移动
                # shutil.move(file, os.path.join(move_path, filename))
                self.cache.hset(f"xdf:video:pathid_{pathId}", vid, json.dumps(info, ensure_ascii=False))
            else:
                # shutil.move(file, os.path.join(move_path, filename))
                print(f"vid:{vid}已经生成过文件，跳过.地址:{generate_mp4_address}")
            # 删除文件
            # os.chdir(final_path)
            # os.system(f"{ffmpeg_path} -i {local_m3u8} -c copy {merge_video_name}")
        else:
            print("未从 redis 中找到匹配数据，video id:", vid)

    async def download_ts(self,ts_name, vid, kb, ib, final_path):
        urlsplit = ts_name.split("?")
        # 这个地方还是变化蛮大的，还是要从 getmvediourl获取到具体的前缀
        if re.search(r"^[A-Z0-9\-]+.ts$", urlsplit[0]):
            url = f"https://media-editor.roombox.xdf.cn/{vid}/transcode/normal/{ts_name}"
        else:
            url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/{vid}/{ts_name}"
        # response = requests.get(url, headers=headers)
        response = await self.xdf_client.get(url)
        if not response.status_code == 200:
            # 再尝试通过这个地址获取看看，如果没有报错
            url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/roombox/10/{vid}/{ts_name}"
            # url = f"https://media-editor.roombox.xdf.cn/clouddriver-transcode/{vid}/{ts_name}"
            r2 = await self.xdf_client.get(url)
            if not r2.status_code == 200:
                print(f"获取 ts 文件请求失败，url={url},返回：{r2.text}")
                return

        desc = AES.new(kb, AES.MODE_CBC, ib).decrypt(response.content)
        ts_file = os.path.join(final_path, urlsplit[0])
        if not os.path.exists(ts_file):
            with open(ts_file, mode="wb") as f3:
                f3.write(desc)
            print("{}->file './{}'".format(threading.currentThread().getName(), urlsplit[0]))
        else:
            print("本地存在ts文件不执行解密下载，", ts_file)
        return urlsplit[0]
#     todo 2.搬运生

