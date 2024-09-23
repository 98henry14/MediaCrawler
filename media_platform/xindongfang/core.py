import asyncio
import os,re
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
from tools import utils
from var import crawler_type_var, source_keyword_var

from .client import XindongfangClient
from .exception import DataFetchError
# from .field import SearchSortType
from .login import XindongfangLogin
from cache.redis_cache import RedisCache


class XindongfangCrawler(AbstractCrawler):
    context_page: Page
    xdf_client: XindongfangClient
    browser_context: BrowserContext

    def __init__(self) -> None:
        self.index_url = "https://study.koolearn.com/my"
        # self.index_url = "https://study.koolearn.com/ky/learning/188924/22666338/19725417"
        # self.user_agent = utils.get_user_agent()
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.cache = RedisCache()
        self.root_path = config.XDF_ROOT_PATH

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

            await self.context_page.goto(self.index_url,wait_until="domcontentloaded")

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
                # record_video_dir="./record/",
                executable_path=executable_path,
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
        await self.context_page.goto(url)
        self.cache.get(key="m3u8_url")

        async with self.context_page.expect_response(re.compile(r'.*\.m3u8.*')) as r2:
            info = await r2.value
            filename = info.request.url.split("?")[0].split("/")[-1]
            text = await info.text()
            utils.logger.info("[XindongfangCrawler.close] 获取m3u8的文件内容 ...",filename)
#             写入到本地文件,todo,记得替换路径,这里也可以直接拿到相关的信息然后往下传递
            async with open(os.path.join("C:\\Users\\xiaoj\\Downloads\\m3u8",filename),"w",encoding="utf-8") as f:
                f.write(text)



    async def handle_all_path(self):
        """
        处理文件目录跟路径
        todo 一个循环搞死吗?
        """
        print(111)
        product = self.cache.hgetall("product:189526")
        product.get('lessonStage').get('344056')


#     todo 1.搬运下载视频的代码
#     todo 2.搬运生

