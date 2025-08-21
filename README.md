# 动漫之家到再漫画的订阅迁移工具

> 临时自用工具,代码有点屎,可能会出现任何bug

## [项目概述] 
这是一个自动化脚本，用于将动漫之家（dmzj）的漫画订阅迁移到再漫画（zaimanhua.com）平台。脚本使用 DrissionPage 库控制 Microsoft Edge 浏览器，自动搜索并订阅用户收藏的漫画。

需要搭配 [dmzj2mihon](https://github.com/heroxv/dmzj2mihon "dmzj2mihon") 项目生成的all_subscriptions.json文件使用

## [使用说明]
1. 通过 [dmzj2mihon](https://github.com/heroxv/dmzj2mihon "dmzj2mihon") 项目获取all_subscriptions.json文件
2. 将获取到的all_subscriptions.json文件放入本项目根目录
3. 尝试运行项目,确保浏览器自动打开,自动化脚本工作
4. 关闭脚本,在自动打开的浏览器中登录 [再漫画](https://manhua.zaimanhua.com/ "再漫画")
5. 重新启动自动化脚本确保正常执行,并等待自动订阅完毕

## [注意事项]
- 确保all_subscriptions.json文件放在根目录下
- 如果浏览器运行错误请尝试更改config.json的浏览器路径
- 在没登录情况下所有漫画都会出现 "漫画不存在或已被删除"
- 如果已经登录有一部分漫画会出现 "漫画不存在或已被删除" 是正常现象
- <img width="387" height="206" alt="image" src="https://github.com/user-attachments/assets/3cda07c2-d9b5-45bb-abcf-9a1342b96440" />
- 有一部分漫画的id会指向别的漫画或者id指向不存在,所以添加了通过名称查找
- <img width="704" height="226" alt="image" src="https://github.com/user-attachments/assets/f94bf3c6-e05e-496d-8979-9a9d49da66a1" />
- 还有些漫画全名查找不出来添加了通过关键词查找
- <img width="1165" height="145" alt="image" src="https://github.com/user-attachments/assets/e64e32b6-0779-4bce-bfa5-d9c8038b65db" />
- 因为是临时自用工具,代码有点屎,可能会出现任何bug
