import asyncio
import functools
import sys
from typing import Optional

from playwright.async_api import BrowserContext, Page
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

import config
from base.base_crawler import AbstractLogin
from cache.cache_factory import CacheFactory
from tools import utils


class XindongfangLogin(AbstractLogin):

    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext,
                 context_page: Page,
                 login_phone: Optional[str] = "",
                 cookie_str: str = ""
                 ):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self, no_logged_in_session: str) -> bool:
        """
            Check if the current login status is successful and return True otherwise return False
            retry decorator will retry 20 times if the return value is False, and the retry interval is 1 second
            if max retry times reached, raise RetryError
        """

        if "请通过验证" in await self.context_page.content():
            utils.logger.info("[XindongfangLogin.check_login_state] 登录过程中出现验证码，请手动验证")

        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        current_web_session = cookie_dict.get("login_token")
        if current_web_session != no_logged_in_session:
            return True
        return False

    async def begin(self):
        """Start login xiaohongshu"""
        utils.logger.info("[XindongfangLogin.begin] Begin login xiaohongshu ...")
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            pass
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            # pass
            await self.login_by_cookies()
        else:
            raise ValueError("[XindongfangLogin.begin]I nvalid Login Type Currently only supported qrcode or phone or cookies ...")

    async def login_by_mobile(self):
        """Login xiaohongshu by mobile"""
        utils.logger.info("[XindongfangLogin.login_by_mobile] Begin login xiaohongshu by mobile ...")
        await asyncio.sleep(1)
        try:
            # 小红书进入首页后，有可能不会自动弹出登录框，需要手动点击登录按钮
            login_button_ele = await self.context_page.wait_for_selector(
                selector="xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button",
                timeout=5000
            )
            await login_button_ele.click()
            # 弹窗的登录对话框也有两种形态，一种是直接可以看到手机号和验证码的
            # 另一种是需要点击切换到手机登录的
            element = await self.context_page.wait_for_selector(
                selector='xpath=//div[@class="login-container"]//div[@class="other-method"]/div[1]',
                timeout=5000
            )
            await element.click()
        except Exception as e:
            utils.logger.info("[XindongfangLogin.login_by_mobile] have not found mobile button icon and keep going ...")

        await asyncio.sleep(1)
        login_container_ele = await self.context_page.wait_for_selector("div.login-container")
        input_ele = await login_container_ele.query_selector("label.phone > input")
        await input_ele.fill(self.login_phone)
        await asyncio.sleep(0.5)

        send_btn_ele = await login_container_ele.query_selector("label.auth-code > span")
        await send_btn_ele.click()  # 点击发送验证码
        sms_code_input_ele = await login_container_ele.query_selector("label.auth-code > input")
        submit_btn_ele = await login_container_ele.query_selector("div.input-container > button")
        cache_client = CacheFactory.create_cache(config.CACHE_TYPE_MEMORY)
        max_get_sms_code_time = 60 * 2  # 最长获取验证码的时间为2分钟
        no_logged_in_session = ""
        while max_get_sms_code_time > 0:
            utils.logger.info(f"[XindongfangLogin.login_by_mobile] get sms code from redis remaining time {max_get_sms_code_time}s ...")
            await asyncio.sleep(1)
            sms_code_key = f"xhs_{self.login_phone}"
            sms_code_value = cache_client.get(sms_code_key)
            if not sms_code_value:
                max_get_sms_code_time -= 1
                continue

            current_cookie = await self.browser_context.cookies()
            _, cookie_dict = utils.convert_cookies(current_cookie)
            no_logged_in_session = cookie_dict.get("web_session")

            await sms_code_input_ele.fill(value=sms_code_value.decode())  # 输入短信验证码
            await asyncio.sleep(0.5)
            agree_privacy_ele = self.context_page.locator("xpath=//div[@class='agreements']//*[local-name()='svg']")
            await agree_privacy_ele.click()  # 点击同意隐私协议
            await asyncio.sleep(0.5)

            await submit_btn_ele.click()  # 点击登录

            # todo ... 应该还需要检查验证码的正确性有可能输入的验证码不正确
            break

        try:
            await self.check_login_state(no_logged_in_session)
        except RetryError:
            utils.logger.info("[XindongfangLogin.login_by_mobile] Login xiaohongshu failed by mobile login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[XindongfangLogin.login_by_mobile] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_qrcode(self):
        """login xiaohongshu website and keep webdriver login state"""
        utils.logger.info("[XindongfangLogin.login_by_qrcode] Begin login xiaohongshu by qrcode ...")
        # login_selector = "div.login-container > div.left > div.qrcode > img"
        qrcode_img_selector = "xpath=//*[@id='p-login-wrap']/div/div/div[3]/div/img"
        # //*[@id='p-login-wrap']/div/div/div[3]/div/img

        # find login qrcode
        base64_qrcode_img = await utils.find_login_qrcode(
            self.context_page,
            selector=qrcode_img_selector
        )
        if not base64_qrcode_img:
            utils.logger.info("没有生成二维码。。。")
            sys.exit()
            # utils.logger.info("[XindongfangLogin.login_by_qrcode] login failed , have not found qrcode please check ....")
            # # if this website does not automatically popup login dialog box, we will manual click login button
            # await asyncio.sleep(0.5)
            # login_button_ele = self.context_page.locator("xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button")
            # await login_button_ele.click()
            # base64_qrcode_img = await utils.find_login_qrcode(
            #     self.context_page,
            #     selector=qrcode_img_selector
            # )
            # if not base64_qrcode_img:
            #     sys.exit()

        # get not logged session
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        no_logged_in_session = cookie_dict.get("login_token")

        # show login qrcode
        # fix issue #12
        # we need to use partial function to call show_qrcode function and run in executor
        # then current asyncio event loop will not be blocked
        partial_show_qrcode = functools.partial(utils.show_qrcode, base64_qrcode_img)
        asyncio.get_running_loop().run_in_executor(executor=None, func=partial_show_qrcode)

        utils.logger.info(f"[XindongfangLogin.login_by_qrcode] waiting for scan code login, remaining time is 120s")
        try:
            await self.check_login_state(no_logged_in_session)
        except RetryError:
            utils.logger.info("[XindongfangLogin.login_by_qrcode] Login xiaohongshu failed by qrcode login method ...")
            sys.exit()

        wait_redirect_seconds = 5
        utils.logger.info(f"[XindongfangLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
        await asyncio.sleep(wait_redirect_seconds)

    async def login_by_cookies(self):
        """login xiaohongshu website by cookies"""
        utils.logger.info("[XindongfangLogin.login_by_cookies] Begin login xiaohongshu by cookie ...")
        for key, value in utils.convert_str_cookie_to_dict(self.cookie_str).items():
            if key != "web_session":  # only set web_session cookie attr
                continue
            await self.browser_context.add_cookies([
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705885.991428,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_ga",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "GA1.2.993296956.1713625335",
        "id": 1
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705886.127113,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_ga_8RBHSP5JM6",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "GS1.2.1727145886.2.0.1727145886.60.0.0",
        "id": 2
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705882.825725,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_ga_MYF8GNFSSR",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "GS1.1.1727145882.11.0.1727145882.0.0.0",
        "id": 3
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705886.528412,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_ga_VE7D9QXBBY",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "GS1.2.1727145886.2.0.1727145886.60.0.0",
        "id": 4
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727145945,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_gat",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "1",
        "id": 5
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727145945,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_gat_UA-16054642-5",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "1",
        "id": 6
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727232285,
        "hostOnly": False,
        "httpOnly": False,
        "name": "_gid",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "GA1.2.1255658797.1727059713",
        "id": 7
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705886.233209,
        "hostOnly": False,
        "httpOnly": False,
        "name": "9dee9d3e36a527e1_gr_cs1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
        "id": 8
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705886.232939,
        "hostOnly": False,
        "httpOnly": False,
        "name": "9dee9d3e36a527e1_gr_last_sent_cs1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
        "id": 9
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727147686,
        "hostOnly": False,
        "httpOnly": False,
        "name": "9dee9d3e36a527e1_gr_last_sent_sid_with_cs1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "33b9aa6c-88d2-4bf1-a1d0-729e55e6fd00",
        "id": 10
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727147686,
        "hostOnly": False,
        "httpOnly": False,
        "name": "9dee9d3e36a527e1_gr_session_id",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "33b9aa6c-88d2-4bf1-a1d0-729e55e6fd00",
        "id": 11
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727147686,
        "hostOnly": False,
        "httpOnly": False,
        "name": "9dee9d3e36a527e1_gr_session_id_sent_vst",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "33b9aa6c-88d2-4bf1-a1d0-729e55e6fd00",
        "id": 12
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705900.833303,
        "hostOnly": False,
        "httpOnly": False,
        "name": "aba0d864c66383b5_gr_cs1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
        "id": 13
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705900.83309,
        "hostOnly": False,
        "httpOnly": False,
        "name": "aba0d864c66383b5_gr_last_sent_cs1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
        "id": 14
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727147700,
        "hostOnly": False,
        "httpOnly": False,
        "name": "aba0d864c66383b5_gr_last_sent_sid_with_cs1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "8e0d5c93-39f9-4726-9d9e-550725319909",
        "id": 15
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727147700,
        "hostOnly": False,
        "httpOnly": False,
        "name": "aba0d864c66383b5_gr_session_id",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "8e0d5c93-39f9-4726-9d9e-550725319909",
        "id": 16
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1727147701,
        "hostOnly": False,
        "httpOnly": False,
        "name": "aba0d864c66383b5_gr_session_id_sent_vst",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "8e0d5c93-39f9-4726-9d9e-550725319909",
        "id": 17
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1729246251,
        "hostOnly": False,
        "httpOnly": False,
        "name": "easeMobId",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "koolearn1725712051456838882",
        "id": 18
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1729246251,
        "hostOnly": False,
        "httpOnly": False,
        "name": "easeMobPassword",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "koolearn1725712051456838882",
        "id": 19
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1761705900.829388,
        "hostOnly": False,
        "httpOnly": False,
        "name": "gr_user_id",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "ccb32893-c33e-44d3-bf15-de1537360181",
        "id": 20
    },
    {
        "domain": ".koolearn.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "Hm_lpvt_5023f5fc98cfb5712c364bb50b12e50e",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "1727145902",
        "id": 21
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1758681901,
        "hostOnly": False,
        "httpOnly": False,
        "name": "Hm_lvt_5023f5fc98cfb5712c364bb50b12e50e",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "1725332527,1726036134,1726639980",
        "id": 22
    },
    {
        "domain": ".koolearn.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "HMACCOUNT",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "34DEDCD166447D6D",
        "id": 23
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1757842707.632978,
        "hostOnly": False,
        "httpOnly": False,
        "name": "kaoyan-0--1",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "0",
        "id": 24
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1757842707.632904,
        "hostOnly": False,
        "httpOnly": False,
        "name": "kaoyan-0-19817254",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "1",
        "id": 25
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1757832592.617128,
        "hostOnly": False,
        "httpOnly": False,
        "name": "kaoyan-0-19833221",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "1",
        "id": 26
    },
    {
        "domain": ".koolearn.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "koo.line",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "study",
        "id": 27
    },
    {
        "domain": ".koolearn.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "login_token",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "login_token_v2_C9E6C9A328E4B0F798B00C23CFAB853E-n2",
        "id": 28
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1760272052.94698,
        "hostOnly": False,
        "httpOnly": False,
        "name": "MEIQIA_TRACK_ID",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "2lk77SJE9RG8hKuAacDrqVEVqZA",
        "id": 29
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1760272052.947866,
        "hostOnly": False,
        "httpOnly": False,
        "name": "MEIQIA_VISIT_ID",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "2lk77SeWZjOACKj4nxhNC30VZN8",
        "id": 30
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1758681901,
        "hostOnly": False,
        "httpOnly": False,
        "name": "mp_ec424f4c03f8701f7226f5a009d90586_mixpanel",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "%7B%22distinct_id%22%3A%20%22%24device%3A191b5dd3c5f6353-09bd6bd13e515b-26001151-1fa400-191b5dd3c5f6353%22%2C%22%24device_id%22%3A%20%22191b5dd3c5f6353-09bd6bd13e515b-26001151-1fa400-191b5dd3c5f6353%22%2C%22%24initial_referrer%22%3A%20%22https%3A%2F%2Flogin.koolearn.com%2Fsso%2FtoLogin.do%3Fnext_page%3Dhttps%253A%252F%252Fstudy.koolearn.com%252Fmy%22%2C%22%24initial_referring_domain%22%3A%20%22login.koolearn.com%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%22%24initial_referrer%22%3A%20%22https%3A%2F%2Flogin.koolearn.com%2Fsso%2FtoLogin.do%3Fnext_page%3Dhttps%253A%252F%252Fstudy.koolearn.com%252Fmy%22%2C%22%24initial_referring_domain%22%3A%20%22login.koolearn.com%22%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%7D",
        "id": 31
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1758681886,
        "hostOnly": False,
        "httpOnly": False,
        "name": "Qs_lvt_143225",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "1725696856%2C1726886797%2C1727145886",
        "id": 32
    },
    {
        "domain": ".koolearn.com",
        "expirationDate": 1758681886,
        "hostOnly": False,
        "httpOnly": False,
        "name": "Qs_pv_143225",
        "path": "/",
        "secure": False,
        "session": False,
        "storeId": "0",
        "value": "2619313347871156000%2C1671800531537438000%2C1672103693951368400%2C3232633384669201000%2C2913506981033691600",
        "id": 33
    },
    {
        "domain": ".koolearn.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "sso.ssoId",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "894308b2e501339019a5e3266c3613532e2c8405e83dda02ca846acde8504cc7f9622194c09e419ef8893c5842fda15e",
        "id": 34
    },
    {
        "domain": ".koolearn.com",
        "hostOnly": False,
        "httpOnly": False,
        "name": "ssoSessionID",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "C9E6C9A328E4B0F798B00C23CFAB853E-n2",
        "id": 35
    },
    {
        "domain": "study.koolearn.com",
        "expirationDate": 1745161298.723312,
        "hostOnly": True,
        "httpOnly": True,
        "name": "__jsluid_s",
        "path": "/",
        "secure": True,
        "session": False,
        "storeId": "0",
        "value": "f3518d5def40528f4af482f8671dfff3",
        "id": 36
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "JSESSIONID",
        "path": "/",
        "secure": False,
        "session": True,
        "storeId": "0",
        "value": "19FBEE398313723FEEDD252073639FCE",
        "id": 37
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "koo-shark-studytools-webapp",
        "path": "/",
        "secure": True,
        "session": True,
        "storeId": "0",
        "value": "6751e3d410e2e861e5be97079fbb8409",
        "id": 38
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "sharks-ui-study",
        "path": "/",
        "secure": True,
        "session": True,
        "storeId": "0",
        "value": "1588ac8ce3e9ec8f530792970a963537",
        "id": 39
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "sharks-webapp-study",
        "path": "/",
        "secure": True,
        "session": True,
        "storeId": "0",
        "value": "DDEFBE32977EC58B2ED389BBCC132B09",
        "id": 40
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "sharks-webapp-study-common-nginx",
        "path": "/",
        "secure": True,
        "session": True,
        "storeId": "0",
        "value": "d06d71f7093e20ec86b012ef1db0ad5e",
        "id": 41
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "sharks-webapp-studyguonei",
        "path": "/",
        "secure": True,
        "session": True,
        "storeId": "0",
        "value": "EAEC9A1563AC3D03DF3F150CD8373530",
        "id": 42
    },
    {
        "domain": "study.koolearn.com",
        "hostOnly": True,
        "httpOnly": True,
        "name": "sharks-webapp-studyguonei-nginx",
        "path": "/",
        "secure": True,
        "session": True,
        "storeId": "0",
        "value": "58ff8b11240b83e6e6ff87bb369b7e74",
        "id": 43
    },{
                'name': key,
                'value': value,
                'domain': ".koolearn.com",
                'path': "/"
            }])
