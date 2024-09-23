import asyncio
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
import re


imgParttern = r'<img.*?src="(.*?)".*?>'
old ='<p><img alt=\"\" src=\"https://guonei-cos.koocdn.com/tiku/2024/05/11/9be688d38b534923941b0371d7d97835.png\" /></p>'
pTagParttern = r'<p>(.*?)</p>'
aa =re.findall(imgParttern,old)
for a in aa:
    print(a)

print(re.sub(imgParttern,lambda x:f"![]({x.group(1)})", old))
t2 = re.findall(pTagParttern,old)[0]
print(t2)
print(re.sub(imgParttern,lambda x:f"![]({x.group(1)})", t2))

exit()
class eventloop:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_forever()
    async def test(i):
        res = asyncio.get_running_loop()
        print(res)
        print(f"hello,{i}")

    def callback(self):
        # 为什么其他两个的方式需要传入async？不传貌似也没关系？
        # 并且如果这个方法被调用不是task = loop.create_task(test('abc'))之后是会报错的
        # 解释？-> call_soon调用普通函数直接传入函数名作为参数，调用协程函数需要讲协程通过loop.create_task封装成task。
        print("Huidiao函数")

    async def my_continue(self):
        print("携程被执行？")

    def run(self):

        loop = asyncio.get_event_loop()

        loop.call_soon(loop.create_task,self.my_continue())



        print(loop._selector)
        task = loop.create_task(self.test('abc'))
        loop.run_until_complete(task)

        loop.call_soon(self.callback())



    def blocking(self):
        import time
        time.sleep(2)
        return "阻塞函数返回-<"

    async def func1(self):
        print("async fun1 run")
        await asyncio.sleep(1)
        print("async fun1 end")

    async def func2(self):
        print("async fun2 run")
        print("调用阻塞函数")
        with ThreadPoolExecutor(max_workers=1) as executor:
            res = await self.loop.run_in_executor(executor,self.blocking)
        # res = await loop.run_in_executor(None,blocking)
            print("async fun2 end ,get result:",res)

    async def test2(self):
        l2 = asyncio.get_event_loop()
        l2.run_until_complete(asyncio.gather(self.func1(),self.func2()))

# image = Image.open("C:\\Users\\xiaoj\\Downloads\\image.png")
#
# # Add a square border around the QR code and display it within the border to improve scanning accuracy.
# width, height = image.size
# new_image = Image.new('RGB', (width + 20, height + 20), color=(255, 255, 255))
# new_image.paste(image, (10, 10))
# draw = ImageDraw.Draw(new_image)
# draw.rectangle((0, 0, width + 19, height + 19), outline=(0, 0, 0), width=1)
# new_image.show()

class asynchttp:
    def __init__(self):
        self.name=''


