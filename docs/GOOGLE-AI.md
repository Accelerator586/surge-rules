# Gemini / NotebookLM routing

`dist/google-ai.list` 将 Gemini、NotebookLM 和 Gemini 开发服务分到 `Gemini` 策略，先于通用 `AI-Services` 和 `Proxy` 规则。节点与地区选择只在本机维护；可在本机设置 `Gemini = select, <preferred proxy>, <alternate proxy>`。

主站能打开不代表消息接口可用。`gemini.google.com` 与 `geminiweb-pa.clients6.google.com` 若走不同出口，可能出现页面可打开但发送消息失败。NotebookLM 同时覆盖 `notebooklm.google`、`notebooklm.google.com`、`notebook.google.com` 等入口，以及专用 API 域名。只验证入口 HTTP 状态不能作为完整使用验证。

## 来源

Antigravity 的主站、专用 API 与 Google AI 编程后端也进入同一分组。实际连接确认其 `language_server` 使用 `aicode.googleapis.com` 和 `daily-cloudcode-pa.googleapis.com`，应用日志还记录了 `jetski-webchannel.googleapis.com`。这些请求先前落到通用代理出口，与 Gemini 分组选定的出口不同。共享的登录和 Play 接口仍保持原有分类。

- [Google 官方 Gemini 防火墙说明](https://knowledge.workspace.google.com/admin/generative-ai/gemini-app/gemini-app-firewall-settings)：说明服务依赖多个主机，连接方式可能随浏览器和网络变化。
- [Google Antigravity 文档](https://antigravity.google/docs/enterprise/)：服务与网络配置参考；本列表只覆盖已纳入维护的公开服务域名，不代表企业部署所需的完整允许列表。
- [MetaCubeX Google Gemini 分类](https://github.com/MetaCubeX/meta-rules-dat/blob/meta/geo/geosite/classical/google-gemini.list)：人工核对后的专用服务域名与 API 主机参考。这里只采用与 Gemini、NotebookLM 及 Gemini 开发服务有关的条目。
- [Gemini](https://gemini.google.com/)、[NotebookLM](https://notebooklm.google.com/)、[NotebookLM 入口](https://notebooklm.google/) 和 [Gemini API 文档](https://ai.google.dev/gemini-api/docs)：公开产品入口和开发文档。

## 范围和维护

规则按公开域名分类，不读取请求内容。Google 登录、字体、头像、YouTube、Drive、广告和统计主机可能与其他产品共享，不能仅凭域名判断请求来自哪个标签页。这些共享主机保留现有分类；本列表不使用整个 `google.com`、`googleapis.com` 或 `clients6.google.com` 后缀，也不启用 MITM。

验证时需要实际打开 NotebookLM 并发送问题，以及在 Gemini 中发送消息并收到回复；随后检查主站和消息接口实际使用的线路。新增专用接口时更新本文件、规则与对应回归案例。此列表覆盖已知服务入口和后端，不能保证未来新域名自动匹配。
