## 获取测试的结果
> 🏷查询列表时，类型 type = 3 为在线测试项目

> **🌿⚠️ requests模块可以直接执行重定向到最后的所需的页面，拿到最后的testResultId即可**
***
搞半天下面的东西没用！!!❗️❗️❗️❗️❗️
```plaintext
1. 先根据获取课程数据的url https://study.koolearn.com/ky/course_kc_data/188924/30427213929/1/0?pathId=342502&nodeId=18799794&level=3&learningSubjectId=101182&_=1726798498740
   - ~~从返回结果中提取到【btnUrl】的值，内容一般长这样子 "/tongyong/test/begin/new-exam/pc/entry?productId=188924&courseId=22666338&nodeId=18799871" 并拼接 https://study.koolearn.com/ 前缀，~~
   - 从返回结果中提取【jumpUrl】，内容一般长这样子 **"/ky/next/188924/30427213929/22666338/18799870/17"** ，拼接前缀**https://study.koolearn.com/**
   - 访问上述例子，默认改接口会直接302跳转到开始页面 **
https://exam.koolearn.com/pc/start-exam?testResultId=226334591174657** 
   - 提取上述的【testResultId】这个就是试卷的id了
   - 再访问 **https://exam.koolearn.com/api/exam-process/v1/answer-sheet/{testResultId}**
 
```

## 获取视频的加密信息
### 1.先获取所有的页面路径，找到叶子节点，并判断类型是属于视频类的，下载m3u8的文件出来

> ⌚️加密难度太大了，需要不断获取hash值，移位操作，循环替换，再进行~😡
> 还不如直接使用playwright获取视频的加密信息，然后保存到本地

```javascript
function h(e, t) {
        o.call(this, "digest"),
        "string" == typeof t && (t = s.from(t));
        for (var r = "sha512" === e || "sha384" === e ? 128 : 64, i = (this._alg = e,
        (this._key = t).length > r ? t = ("rmd160" === e ? new l : c(e)).update(t).digest() : t.length < r && (t = s.concat([t, u], r)),
        this._ipad = s.allocUnsafe(r)), n = this._opad = s.allocUnsafe(r), a = 0; a < r; a++)
            i[a] = 54 ^ t[a],
            n[a] = 92 ^ t[a];
        this._hash = "rmd160" === e ? new l : c(e),
        this._hash.update(i)
    }
```