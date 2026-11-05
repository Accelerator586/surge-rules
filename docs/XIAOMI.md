# 小米服务与 macOS 小米互联服务

`rules/cn.list` 显式维护小米账号、互联、设备 API、推送及资源域名，统一进入 `CN` 分组。CN 选择 DIRECT 时，这些正常服务直接连接。公共域名根据 [blackmatrix7 的 XiaoMi 列表](https://github.com/blackmatrix7/ios_rule_script/blob/master/rule/Surge/XiaoMi/XiaoMi.list) 及已安装应用的公开服务地址交叉核对；未整套导入上游的 IP 或进程规则。

应用包含的服务地址例如 `account.xiaomi.com`、`api.account.xiaomi.com`、`cn-device.interconnect.miui.com` 和 `hyperos.mi.com`，均由对应根域名后缀规则覆盖。

## 要求整个互联应用直连时

对于用户明确要求整个应用通过 CN 的场景，可在本机配置的 `[Rule]` 中加入：

```ini
PROCESS-NAME,/Applications/小米互联服务.app/*,CN
```

将它放在本机必要的家庭网段 / 局域网规则之后、所有广告拦截规则之前。匹配限定到该应用包的完整路径，包含它的辅助进程；不要使用宽泛的 `mi` 或 `xiaomi` 关键词匹配所有进程。

这条例外仅在本机维护，不会被生成到公共 `dist/*.list` 中。它将该应用的公共 IP 连接、未收录域名及自身统计请求一并交给 CN；应用以外的请求仍按原广告规则和最终代理规则处理。若应用安装位置变化，需更新路径。

局域网发现和设备连接还受系统权限、设备所在网络及无线状态影响；分流规则只能决定 Surge 已接管连接的出口，不能替代这些条件。
