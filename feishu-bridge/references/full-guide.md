# 飞书桥接全流程指南

本文是 `feishu-bridge` skill 的深度参考。上层 `SKILL.md` 决定何时触发和先做什么；本文保存从实测中来的完整顺序、证据和排错细节。

## 1. 已验证的形态

已在本机 Muse 环境完整跑通的链路（2026-10-07，中国飞书）：

1. 用户私聊机器人发文字，飞书长连接把 `im.message.receive_v1` 推给 daemon。
2. daemon 按 `message_id` 去重、白名单过滤，把标准化 JSON 写入 `queue/inbox`。
3. inbox hook 每 15 秒发现文件，唤醒工作者生成回复 JSON 到 `queue/outbox`。
4. daemon 每 2 秒扫 outbox，按 `chat_id` 发回飞书；用户端确认收到。
5. 保活三层：daemon 内 WS 断开重连循环 + 15 秒心跳；supervisor 杀子进程后 3 秒起拉、约 7 秒重新连上 WS；health hook 每 60 秒查心跳，超过 120 秒唤醒运维工作者自动跑 `start_bridge.sh`。
6. 附件三类实测成功：文本文件（file）、PNG 图片（image）、MP4 视频（media）。开通上传权限前得到过 99991672，MP4 按 file 发得到 230055，改 media 后成功。
7. 首条私聊回复实测延迟约 32 秒（入队 18:09:03，发回 18:09:35），这是轮询+工作者延迟，不是即时直连，报告时必须诚实标注量级。

未实测、不得声称完成：国际版 Lark、群聊端到端、卡片交互、接收用户发来的图片/文件、在飞书里承接浏览器接管或 Muse 原生审批。

## 2. 为什么不用原生通道或 Webhook

- 本机 Muse 原生消息侧通道当时只有 WhatsApp；飞书没有原生通道，只能自建桥接。若未来平台新增原生飞书，先停下来重估，不要无条件沿用本桥。
- 长连接不需要公网域名、回调验签服务或内网穿透，适合宿舍/本地 VM/代理网络。若部署环境能稳定提供 HTTPS 回调，可另行评估 Webhook，但本模板代码按长连接写，两种事件入口不要混跑造成重复消费。

## 3. 飞书后台配置的证据来源

不要只听“我好像开过了”。每个开关都用 API 返回或真实事件验收：

| 后台项 | 用来证明它的证据 |
|---|---|
| 机器人能力与可用范围 | 用户能在飞书中找到机器人并私聊；机器人信息接口成功 |
| `im:message.p2p_msg:readonly` | 私聊消息真的进入 inbox |
| 长连接 + `im.message.receive_v1` | daemon 日志显示 WS 已连上且能入队 |
| `im:message:send_as_bot` | outbox 文字发送日志 code 0 且用户端收到 |
| `im:resource:upload` 或 `im:resource` | 三类附件 upload + send 均 code 0 且用户端打开 |
| 群 @ 权限与事件 | 群里未 @ 不入队、@ 后入队并回复（启用群聊时才验） |

权限改完后，有的租户要点“创建版本并发布”才生效。验收仍失败时先查已发布版本的权限快照，不要在本地反复重启撞运气。

## 4. 凭证处理：这次踩过的坑

- Feishu 需要 App ID + Secret 一起放进 JSON 请求体换 `tenant_access_token`。只有“一个秘密值”的录入卡无法描述这对凭证；2026-10-07 的一次安全库 API 录入尝试就因此被拒。
- Secret 只用所有者原文做一次复制并立刻校验。不要从记忆默写，不要去翻聊天记录回捞后转手。曾出现长得像、末尾多两个字符的转写，结果先被 WS 拒 1000040345，后被 token 接口拒 10014。遇到 invalid：停掉所有自动重试进程，报告精确 code，请所有者将 Secret 单独一行重发。
- 日志、报告、长期记忆、skill、代码、命令参数都不能出现 Secret 或完整 token。WS 的 SDK INFO 日志会带连接地址和 ticket，汇报时只能说“已连上”，不能摘抄那一行。
- 两种凭证模式只能由所有者在听清差别后选：
  - `memory_only`：Secret 经 stdin 进入 supervisor 内存，子进程复活不需要重新给；supervisor 或整台机器死了就必须补发，health hook 只负责提醒。
  - `local_file`：所有者明确接受把小号/低风险机器人凭证放运行目录 `credentials.json`（0600、.gitignore），supervisor 可在 supervisor 死亡和整机重启后自启。这是所有者对自己机器的决定，不得替高价值生产应用默认套用。
- 凭证文件不得随 skill 分发，不得复制进模板，不得写到 systemd unit、环境文件、启动命令参数。

## 5. 网络与代理

- 本机出网经环境代理。`lark-oapi` 的 WS 客户端曾强行给 websockets 传 `proxy=None`，在该环境出现 `SSL: WRONG_VERSION_NUMBER`。模板已把 `_ws_connect_kwargs` 改回 `{"proxy": True}` 让 websockets 按环境发现代理。
- 若新环境直连正常，这段补丁应是无害的默认发现；若仍走代理，永远不要把代理 URL 或其中的凭据写进日志和报告。
- 排查顺序：先分开验证 REST token（HTTP）与 WS（长连接）。token 通不等于 WS 通；WS 报错先看 SDK 异常类型和飞书 code，不要把所有失败归咎于 Secret。

## 6. 进程模型与边界

- supervisor 是保活边界：它持有凭证、启动子进程、监视心跳、退避重启、响应自己的 SIGTERM 后杀子进程。supervisor 的进程会话若被运行平台清掉，单靠这层无法复活，所以必须再有 health hook、cron、或 systemd 之一盯着。
- system 型续命要选运行平台真正会拉起和监管的机制。用 systemd 时，把 `ops/feishu-bridge.service.example` 复制、改路径后，还要验证 `systemctl --user daemon-reload`、开机目标以及 VM 替换后的实际重拉，不能只说 unit 文件在。
- Muse hooks 的 state 只供脚本去重/抑重复唤醒。hook 脚本不能放凭证，不直接发飞书消息。
- inbox hook 的工作者可能被同一文件唤醒两次（文件尚未移走时），模板靠 outbox 文件名固定 + 发送后移 processed 控制重复；验收时要看 daemon 只实际发送一次。如新平台会并行启动多个工作者，先补 inbox claim/锁机制再上线，不要假设天然单线程。
- daemon 的白名单每条消息时重读 `config.json`（模板代码已实现），所以回填后无需重启。然后再做一条白名单外测试，如果有可用的第二个账号，否则在报告里标未测，不要编造。

## 7. 附件实现注意

- 图片：`POST /open-apis/im/v1/images`，字段 `image_type=message`，取 `image_key`，再发 `msg_type=image`。
- 普通文件：`POST /open-apis/im/v1/files`，`file_type` 按后缀映射（pdf/doc/xls/opus/mp4 用对应值，其余 stream），取 `file_key`，除 MP4 外发 `msg_type=file`。
- 视频：MP4 上传拿到的 `file_key` 不能再按普通 file 消息发，会报 230055 类型不匹配，必须发 `msg_type=media`。需要视频封面时另传图片取 `image_key` 再放入 media 内容，模板默认不强加封面。
- 大小限制和可播编码会随飞书版本/租户变化，本模板只验过 KB 级 txt/png 和 3 秒 640x360 H.264 MP4。大文件、长视频、opus/docx 先小样验，再在报告里给实际大小和格式，不要拿“小文件成功”推销“任意视频都行”。
- `last_send_error.json` 是最后一次失败快照，可能比当前运行旧。查失败时先比对文件修改时间与 daemon 日志时间。

## 8. 飞书侧工作边界

- 飞书适合随身交代文字、已约定的轻量编辑、收成品附件和离线提醒。
- 浏览器画面看不到、不能接管点按；Muse 主界面的结构化审批卡、安全录入和钱包确认不能用一句飞书文字“确认”代替。涉及付款、向外发送、公开发布、重要删除或高价值账号设置，桥接工作者只能停下并让用户回主界面确认。
- 这条边界由所有者要求和任务风险一起定：用户可以扩大或收窄轻量工作的范围，但不能把平台原生审批本身搬进飞书。

## 9. 排错表

| 现象 | 先查 | 不要做 |
|---|---|---|
| token 或 WS 报 secret invalid | 停重试，查 code（10014/1000040345），请所有者单独一行重发并立即校验 | 凭记忆重敲、从历史记录回捞、连续重启碰运气 |
| 99991672 | 按 msg 里缺的 scope 去后台补开并发布；区分私聊、群信息、资源上传三种缺口 | 把它说成代码 bug 而反复改发送逻辑 |
| WS `WRONG_VERSION_NUMBER` | 检查代理发现与 SDK 的 proxy 设置，REST/WS 分开验 | 记录或转发代理 URL |
| 230055 | 多半是 mp4 用了 file 消息，改 media | 换小视频反复试同一错误路径 |
| 进程消失但队列有消息 | 先看 supervisor/daemon 心跳、supervisor 日志，再决定拉起 | 直接再启第二个 daemon 造成重复发信 |
| API code 0 但用户没看到 | 检查是否发到正确 chat_id、机器人可用范围和用户端的会话 | 直接重复发送三遍 |
| 杀子进程后不复活 | 看 supervisor 是否还活着、退避时间、凭证文件是否可读（只查存在和权限，不看内容） | 杀 supervisor 后只怪 daemon |
| 整机重启后没恢复 | 看 health/cron/systemd 的实际唤醒证据；memory 模式需要所有者补发 | 声称心跳文件在就等于进程在 |

## 10. 停止与回滚

1. 先停健康和 inbox hook 或等价的轮询器，避免运维工作者又把桥拉起来。
2. 只停本桥的 supervisor 进程树，再用进程列表确认 daemon 也退出。
3. 保留队列、日志和 state 做审计；未经所有者批准，不删除 `credentials.json`、不禁用飞书应用。
4. 若要彻底废弃：所有者在飞书后台重置/作废 Secret 并下线应用版本，运维 Agent 再按指示清理本地凭证和计划任务，并把清理证据（文件不存在、计划已停）写进报告。
