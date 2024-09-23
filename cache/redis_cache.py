# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Name    : 程序员阿江-Relakkes
# @Time    : 2024/5/29 22:57
# @Desc    : RedisCache实现
import json
import pickle
import time
from typing import Any, List

from redis import Redis

from cache.abs_cache import AbstractCache
from config import db_config
from typing import Optional


class RedisCache(AbstractCache):

    def __init__(self) -> None:
        # 连接redis, 返回redis客户端
        self._redis_client = self._connet_redis()

    @staticmethod
    def _connet_redis() -> Redis:
        """
        连接redis, 返回redis客户端, 这里按需配置redis连接信息
        :return:
        """
        return Redis(
            host=db_config.REDIS_DB_HOST,
            port=db_config.REDIS_DB_PORT,
            db=db_config.REDIS_DB_NUM,
            password=db_config.REDIS_DB_PWD,
        )

    def get(self, key: str) -> Any:
        """
        从缓存中获取键的值, 并且反序列化
        :param key:
        :return:
        """
        value = self._redis_client.get(key)
        if value is None:
            return None
        return pickle.loads(value)

    def set(self, key: str, value: Any, expire_time: int) -> None:
        """
        将键的值设置到缓存中, 并且序列化
        :param key:
        :param value:
        :param expire_time:
        :return:
        """
        self._redis_client.set(key, pickle.dumps(value), ex=expire_time)

    def keys(self, pattern: str) -> List[str]:
        """
        获取所有符合pattern的key
        """
        return [key.decode() for key in self._redis_client.keys(pattern)]

    def setStr(self, key: str, value: Any) -> None:
        """
        将键的值设置到缓存中, 并且序列化
        :param key:
        :param value:
        :param expire_time:
        :return:
        """
        self._redis_client.set(key, json.dumps(value, ensure_ascii=False))


    def getStr(self,key:str):
        return self._redis_client.get(key)

    def hset(self,name: str, key: Optional[str] = None, value: Optional[str] = None,):
        self._redis_client.hset(name, key, value)
    def hget(self,name: str,key: str):
        return self._redis_client.hget(name,key)

    def hgetall(self,name: str):
        return self._redis_client.hgetall(name)

    def exists(self,key:str):
        return self._redis_client.exists(key)


if __name__ == '__main__':
    redis_cache = RedisCache()
    # basic usage
    # redis_cache.set("name", "程序员阿江-Relakkes", 1)
    # print(redis_cache.get("name"))  # Relakkes
    # print(redis_cache.keys("*"))  # ['name']
    # time.sleep(2)
    # print(redis_cache.get("name"))  # None
    #
    # # special python type usage
    # # list
    # redis_cache.set("list", [1, 2, 3], 10)
    # _value = redis_cache.get("list")
    # print(_value, f"value type:{type(_value)}")  # [1, 2, 3]
    data = [{
        "productId": 166089,
        "productName": "2025考研计算机全程班",
        "url": "/tongyong/course/166089/30427213929",
        "lessonStage": [
            {"id": 248695, "name": '择校备考指导', "learnModel": 0 },
            {"id": 248696,"name": '基础精讲',"learnModel": 0},
            {"id": 248697,"name": '习题带刷',"learnModel": 0},
            {"id": 248698,"name": '真题解析',"learnModel": 0},
        ]
    },{
        "productId": 188924,
        "productName": "2025考研英语全程班 春季班",
        "url": "/tongyong/course/188924/30427213929",
        "lessonStage":[
            {"id":342374, "name":'开班导学', "isSmartMode":False, "learnModel":0},
            {"id":383957, "name":'【宠粉关怀：节点提醒&考前点睛&福利课堂】', "isSmartMode":False, "learnModel":0},
            {"id":342502, "name":'基础起步', "isSmartMode":False, "learnModel":0},
            {"id":342378, "name":'【慧学】诊断课（英语二）', "isSmartMode":False, "learnModel":2},
            {"id":342380, "name":'强化刷题（经典真题）', "isSmartMode":False, "learnModel":0},
            {"id":342381, "name":'强化刷题（近年真题）', "isSmartMode":False, "learnModel":0},
            {"id":342382, "name":'模考冲刺', "isSmartMode":False, "learnModel":0},
            {"id":342383, "name":'考前点睛', "isSmartMode":False, "learnModel":0},
            {"id":342375, "name":'择校择专业指导', "isSmartMode":False, "learnModel":0},
            ]
    },{
        "productId": 189526,
        "productName": "2025考研数学全程班 春季班",
        "url": "/tongyong/course/189526/30427213929",
        "lessonStage": [
            {"id": 386014, "name": '宠粉关怀：节点提醒&考前点睛&福利课堂', "isSmartMode": False, "learnModel": 0},
            {"id": 344053, "name": '导学', "isSmartMode": False, "learnModel": 0},
            {"id": 344056, "name": '数学二', "isSmartMode": False, "learnModel": 0},
            {"id": 344057, "name": '【慧学】诊断', "isSmartMode": False, "learnModel": 2},
            {"id": 387818, "name": '强化补弱课', "isSmartMode": False, "learnModel": 0},
            {"id": 344060, "name": '择校择专业课程', "isSmartMode": False, "learnModel": 0},
        ]
    },{
        "productId": 188975,
        "productName": "2025考研政治全程班 春季班",
        "url": "/tongyong/course/188975/30427213929",
        "lessonStage": [
            {"id": 387358, "name": '【宠粉关怀：节点提醒&考前点睛&福利课堂】', "isSmartMode": False, "learnModel": 0},
            {"id": 341884, "name": '政治', "isSmartMode": False, "learnModel": 0},
            {"id": 356137, "name": '慧学诊断', "isSmartMode": False, "learnModel": 2},
            {"id": 341883, "name": '择校择专业', "isSmartMode": False, "learnModel": 0},
        ]
    }
    ]
    for dt in data:
        productId = dt.get('productId')
        for key,value in dt.items():
            redis_cache.hset(f"xdf:product:{productId}",key,json.dumps(value,ensure_ascii=False))
