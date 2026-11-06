# Firebase / Google Analytics 控制台

外部广告规则中的 `DOMAIN-KEYWORD,analytics.` 会匹配 `analytics.google.com` 和 `firebaseanalytics.googleapis.com`。如果广告规则位于普通 Google 代理规则之前，浏览器可能显示连接意外关闭；请求被 Surge 拒绝时并没有到达 Google。

`rules/proxy-allow.list` 为控制台和开发 API 维护精确的 DOMAIN 例外，使用现有 Proxy 分组。生成订阅必须位于所有外部广告规则之前，并携带 no-resolve。不要将整个 google.com 或 googleapis.com 后缀提前放行。

这里的开发控制台/API 例外不包含 `www.google-analytics.com`、`googlesyndication.com`、`googleadservices.com` 等通用采集或广告域名，也不放行 Firebase 其他应用的遥测域名。

例如：

```ini
RULE-SET,https://raw.githubusercontent.com/Accelerator586/surge-rules/main/dist/proxy-allow.list,Proxy,no-resolve,update-interval=3600
```

验证应包含控制台精确域名经 Proxy 转发、广告域名仍被拒绝、相似但无关域名不获得例外，以及不带登录凭据的 HTTPS 请求能完成 TLS / 跳转。未登录请求的成功不能证明具体项目权限或登录会话正常。
