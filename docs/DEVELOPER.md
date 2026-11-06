# 开发者控制台、登录和数据接口

`rules/proxy-allow.list` 是开发者服务的精确域名列表，引用时交给独立 Developer 分组，并放在外部广告规则之前。当前覆盖 42 个域名，每个域名的公开来源或主机名级运行证据保存在 `developer-sources.json`。

## 覆盖范围

| 平台 | 范围 |
| --- | --- |
| Firebase / Google Analytics | 控制台、分析报表、Crashlytics 查询、项目管理、Firestore、Storage、Hosting、Remote Config、Rules、App Distribution、认证，以及已观察到的控制台 RPC 主机 |
| Google Play | Play Console、Android Publisher、Developer Reporting 和已观察到的上架/受众/健康/统计 RPC 主机 |
| Samsung Galaxy Store | Seller Portal、开发者文档、三星账号登录、Seller Portal 图片资源、Developer API；官方 API 包含应用发布和 GSS 统计能力 |

认证和数据接口被单独列入，避免只放行控制台首页却继续拦截页面的数据请求。普通广告采集、Firebase 遥测及 Crashlytics 客户端上报域名没有整体放行；开发者查询接口与客户端采集主机按精确域名区分。

## 本机接入

```ini
[Proxy Group]
Developer = select, Master-Router

[Rule]
# 保留必要的本机/私人规则和已有的应用级例外。
RULE-SET,https://raw.githubusercontent.com/Accelerator586/surge-rules/main/dist/proxy-allow.list,Developer,no-resolve,update-interval=3600
# 外部广告规则和普通服务规则放在后面。
```

以上是配置片段，需合入已有分组和规则。主线路切换时 Developer 默认跟随；也可给 Developer 单独增加已有的代理节点选项。旧配置继续使用 Proxy 策略也保持兼容。

此前明确指定“整个微信/小米互联应用直连”的进程例外仍可保留在前面。因此，从微信内置网页打开控制台仍遵守微信的应用级选择；系统浏览器中的开发者请求使用 Developer。

## 验证及限制

- 自动检查将已知的分析、Crashlytics 和商店后台接口模拟为被广告规则拦截的对象，验证精确开发者规则仍先命中。
- 新增开发者域名必须同步补充来源记录，否则构建失败。不得用整个 google.com、googleapis.com 或 samsung.com 后缀替代精确名单。
- 本机还需检查实际 Surge 规则顺序及出口。公共入口返回 HTTP 200、API 无凭据时返回授权错误，都只能证明部分连通性；不能证明项目权限、登录会话和真实数据图表加载正常。
- 这是一份可维护的基线，不承诺覆盖平台今后的所有内部主机。发现数据图表异常时，应检查具体被拦截的接口，再补精确域名及回归案例。

## 主要官方参考

- [Firebase Management API](https://firebase.google.com/docs/reference/firebase-management/rest)
- [Firebase Crashlytics API](https://firebase.google.com/docs/reference/crashlytics/rest)
- [Firebase Authentication REST API](https://firebase.google.com/docs/reference/rest/auth)
- [Google Play Developer API](https://developers.google.com/android-publisher/api-ref/rest)
- [Google Play Developer Reporting API](https://developers.google.com/play/developer/reporting/reference/rest)
- [Galaxy Store Developer API](https://developer.samsung.com/galaxy-store/galaxy-store-developer-api/use-the-access-token.html)
