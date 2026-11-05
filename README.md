# Surge rules

面向“已知 CN 服务独立分组、分类时不主动解析、未知流量走最终代理”的个人规则仓库。

本仓库负责规则分类。节点、密码、家庭网段、私人域名、端口转发和 Surge 功能设置保留在本机。

## 分流约定

| 文件 | Surge 分组 | 用途 |
| --- | --- | --- |
| `dist/cn-allow.list` | `CN` | 已确认的广告误拦截例外，放在外部广告规则前 |
| `dist/reject.list` | `REJECT` | 少量个人广告拦截补充 |
| `dist/ai.list` | `AI-Services` | AI 服务及已有的 Discord / Midjourney 分类 |
| `dist/apple.list` | `Apple` | Apple 服务 |
| `dist/parsec.list` | `Parsec` | Parsec 服务 |
| `dist/encrypted-sni.list` | `EncryptedSNI` | encryptedsni.com |
| `dist/proxy.list` | `Proxy` | 通用代理例外，防止被后面的 CN 规则放行 |
| `dist/cn.list` | `CN` | 已知国内服务的域名与域名后缀 |

发布列表只包含 `DOMAIN` 和 `DOMAIN-SUFFIX`。不发布关键词、整进程直连、GEOIP、ASN、IP 地址段或嵌套远程订阅规则。单标签顶级域、宽泛的 `com.cn` 等公共后缀以及部分共享云平台后缀也被排除。具体排除项见 `policy.json`。

这是偏保守的直连白名单。域名遗漏会走最终代理；它不承诺所有国内站点均直连，也不根据请求发生时的 IP 所在地推断服务归属。

## 在 Surge 中使用

1. 保留本机的 `[Proxy]` 和 `[Proxy Group]`，确认存在上表的分组。分组的直连/代理选择仍由本机控制。
2. 保留本机的局域网、回家网段和私人例外；IP 规则引用保持 `no-resolve`。
3. 将 `dist/surge-rules.conf` 中的规则加入现有 `[Rule]`。其中 `cn-allow.list` 必须放在所有外部广告规则之前，其他订阅放在外部广告规则之后。它是规则片段，不是完整配置，也不能作为模块导入。
4. 保留现有 Figma 专属规则，并放在通用代理/CN 规则之前。移除被替换的旧 CN/AI/Apple 订阅，以免旧的宽泛直连规则继续抢先命中。
5. `[Rule]` 只有一个最后的 `FINAL,Proxy,dns-failed`。使用规则模式。

订阅文件基址：

`https://raw.githubusercontent.com/Accelerator586/surge-rules/main/dist/`

示例：

```ini
RULE-SET,https://raw.githubusercontent.com/Accelerator586/surge-rules/main/dist/cn.list,CN,no-resolve,update-interval=3600
```

完整广告拦截并未包含在仅有少量补充的 `reject.list` 中。可继续单独订阅一套广告主规则，放在 `cn-allow.list` 之后、其他服务规则之前，并避免同时堆叠多套广告主规则。仅将已确认的误拦截域名放入 `rules/cn-allow.list`，不要将整个 CN 集合移到广告规则前。仓库不启用 MITM，也不修改本机的解密设置。

`dist/validation.conf` 仅用于 Surge 语法检查。它将所有组指向 DIRECT，不能用作生产代理配置。

## DNS 边界

域名分类不做真实 DNS 查询。已选定 DIRECT 的请求仍须解析目标域名；代理节点自身也可能需要解析。这里不承诺所有应用、所有协议均零 DNS/IP 泄露。应用自行使用 DoH、增强模式的排除路由等问题，需要在本机单独审计。

## 编辑和验证

需要 Python 3.9+，无第三方依赖。

```sh
python3 scripts/rules.py build
python3 scripts/rules.py check
python3 -m unittest discover -s tests -v
python3 scripts/rules.py explain api2.cursor.sh
python3 scripts/rules.py explain unrelated-baidu-check.invalid
```

编辑 `rules/*.list`，不要手工编辑 `dist/`。规则文件不带策略名称，例如 `DOMAIN-SUFFIX,cursor.com`。`policy.json` 决定发布顺序、组名和排除项。

在装有 Surge 的 Mac 上再运行：

```sh
/Applications/Surge.app/Contents/Applications/surge-cli --check "$PWD/dist/validation.conf"
```

本地解释器只验证本仓库的域名分类；本机私人规则、外部广告规则和 Surge 功能开关仍须用 `surge-cli rule explain` 检查最终效果。

## 上游维护

- `vendor/sukka/` 保存实际采用的原始字节；`sources.lock.json` 保存 SHA-256、来源和初始版本。
- `scripts/rules.py build` 完全离线，先验证原始文件哈希，再提取允许的域名类型、过滤、去重并生成发布文件。
- 每周一北京时间 06:17，GitHub Actions 尝试读取上游，运行检查，再创建或更新 `automation/upstream-update` 分支的 PR。有变化才提案，下载/校验失败则任务失败并保留 main 的旧版本。
- **不自动合并。** 更新报告完整列出新增和删除的规则。CN 新增条目扩大直连范围，须重点审阅。
- 定时工作流只更新 vendor、锁文件、dist 和更新报告，不修改构建代码和分流策略。
- GitHub Actions 若使用默认 GITHUB_TOKEN 创建 PR，GitHub 可能不会为该机器人 PR 再触发另一次 PR 检查；更新任务已在推送前执行同样的检查。仍应审阅差异；需要时可手工对该分支运行验证工作流。
- 仓库设置需允许 GitHub Actions 创建 PR；若被账号/组织策略禁止，工作流会明确失败，不回退为直接写 main。

手工检查上游：

```sh
python3 scripts/rules.py update
python3 scripts/rules.py check
python3 -m unittest discover -s tests -v
```

## 维护请求

小米账号、互联和设备服务进入 CN。macOS“小米互联服务”的整个应用直连例外及其作用范围，见 [小米服务说明](docs/XIAOMI.md)。

微信主程序、内置网页、小程序和辅助进程整体通过 CN 的本机例外，见 [微信服务说明](docs/WECHAT.md)。

可以在 GitHub 提交 Routing correction issue，也可以在 Codex 中说明“哪个公开域名应进入哪个组”。维护时补充规则和对应的回归案例，检查通过后提交 PR。

新增直连例外需要说明服务归属。不要为修复一个子域名而直接放行整个平台、共享云后缀或应用的全部进程流量。

## 来源与许可

通用域名来源于 Sukka 及贡献者维护的 [SukkaW/Surge](https://github.com/SukkaW/Surge)，本仓库对数据进行了过滤和补充。许可及具体修改见 `LICENSE` 和 `NOTICE.md`。本项目不暗示上游作者认可个人分流策略。
