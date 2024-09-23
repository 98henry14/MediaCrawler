#!/opt/homebrew/Frameworks/Python.framework/Versions/3.9/bin/
# -*- codig:utf-8 -*-
import execjs
import subprocess
import re
res = subprocess.run("ac %PATH%",check=True,shell=True,stdout=subprocess.PIPE,text=True,stderr=subprocess.PIPE)
print(res.returncode,res.stdout.strip(),res.stderr.strip())

if re.search(r"^[A-Z0-9\-]+.ts$", "2dee2e19fa4e4056a3ae0bb6436f671f-00008.ts"):
    print("匹配成功")
else:
    print("匹配失败")


exit()
# 定义 JavaScript 代码
js_code = """
const crypto = require('crypto');

function computeHMAC(secretKey, message) {
    const hmac = crypto.createHmac('sha1', secretKey);
    hmac.update(message);
    return hmac.digest('hex');
}

computeHMAC;
"""

# 编译 JavaScript 代码
js_runtime = execjs.compile(js_code)

# 定义数据
secret_key = 'mySecretKey'
message = 'Hello World'

# 传递数据并执行 JavaScript 函数
result = js_runtime.call('computeHMAC', secret_key, message)

# 打印结果
print(result)


msg = "{\"definition\":\"SD,LD,FD,HD,2K,4K,OD,SQ,HQ,AUTO\",\"enc_type\":0,\"stream_type\":\"\",\"url_type\":0,\"video_id\":\"9754da30596a71ee919df6f6c5596302\",\"exclude_enc_type\":[0]}"
key = "1cbd1678bf09d5966ca2399fd35dae10"
a1 = hashlib.sha1(key.encode("utf-8"))
a31 = a1.hexdigest()
u8 = msg.encode('utf-8')
a2 = a1.update(u8)
# a2 = a1.update(msg)
a3 = a1.digest().hex()

# 字节转字符串
# a1 = hmac.new("sha1","{\"definition\":\"SD,LD,FD,HD,2K,4K,OD,SQ,HQ,AUTO\",\"enc_type\":0,\"stream_type\":\"\",\"url_type\":0,\"video_id\":\"9754da30596a71ee919df6f6c5596302\",\"exclude_enc_type\":[0]}","5178edd38d47a051a2a065a905ac28de")
# a2 = a1.hexdigest()
# a1 = hmac.new("5178edd38d47a051a2a065a905ac28de","{\"definition\":\"SD,LD,FD,HD,2K,4K,OD,SQ,HQ,AUTO\",\"enc_type\":0,\"stream_type\":\"\",\"url_type\":0,\"video_id\":\"9754da30596a71ee919df6f6c5596302\",\"exclude_enc_type\":[0]}",hashlib.sha1)
# a2 = a1.hexdigest()
# a3 = a2
# # a2 = a1.update("{\"definition\":\"SD,LD,FD,HD,2K,4K,OD,SQ,HQ,AUTO\",\"enc_type\":0,\"stream_type\":\"\",\"url_type\":0,\"video_id\":\"9754da30596a71ee919df6f6c5596302\",\"exclude_enc_type\":[0]}")
# # a3 = a1.digest("hex")
print(a1)
print(a2)
print(a3)
print(a31)
print(bytes(a31.encode('utf-8')))
exit()
