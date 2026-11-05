# 微信整个应用通过 CN

`rules/cn.list` 显式维护微信的公开服务域名，包括 `servicewechat.com`、`wechat.com`、`weixin.com` 等，补充来源于 [WeChat 服务列表](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Surge/WeChat/WeChat.list)。不引入上游 IP、ASN 或关键词规则。

用户明确要求整个微信应用通过 CN 时，本机 `[Rule]` 中可使用：

```ini
PROCESS-NAME,/Applications/WeChat.app/*,CN
```

放在必要的局域网 / 家庭网段规则之后、广告拦截规则之前。完整应用路径覆盖 WeChat 主程序、WeChatAppEx、WeChatAppEx Helper、WeApp 小程序及应用包内的其他辅助进程；不要使用通用的 Helper 或 Updater 进程名。

部分版本的专属 Sparkle 更新器在用户缓存目录中运行。需要时，根据已确认的真实进程路径，在本机额外限定到 `Library/Caches/com.tencent.xinWeChat/org.sparkle-project.Sparkle/` 下的 Updater.app；个人绝对路径不发布到此仓库。

应用规则覆盖公网 IP、UDP/QUIC、未收录域名、微信内置网页/小程序的外部站点，以及自身统计请求。CN 选择 DIRECT 时，这些请求都直连；其他应用仍使用原广告规则和 FINAL 代理。将外部站点交给系统浏览器打开后，流量按系统浏览器本身的规则处理。

规则变更对新连接生效。原有代理连接可在确认属于微信后单独断开，让应用自动重连；无需重启 Surge 或中断其他应用。
