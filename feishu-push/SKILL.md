---
name: "feishu_push"
description: "通过飞书自建应用机器人向群聊发送消息：用 App Secret 换取 tenant_access_token 后调用飞书消息 API。触发词：飞书推送、往飞书发消息、飞书群发。"
---

# 飞书消息推送

## Purpose
按需或定时向飞书群聊推送文本消息。CLI 负责用保险库中的 App Secret 经 authd 凭据代理换取 tenant_access_token，再调用 open.feishu.cn 消息接口发送。

## Tooling
`bin/feishu_send.py` sends a text message to a group chat:

```
python3 ~/workspace/skills/feishu-push/bin/feishu_send.py --text "消息内容" [--chat-id oc_xxx]
```

It fetches an `hsurr:*` surrogate for connector `custom.feishu` from authd,
appends it as the `app_secret` query parameter on Feishu's
`tenant_access_token` endpoint (Feishu accepts `app_id`/`app_secret` as query
params — verified), exchanges it for a short-lived `tenant_access_token`, and
POSTs to `im/v1/messages`. Default `--chat-id` is the user's 「每日新闻」群
(`oc_de457d893dbbe148335a2bf8508da50a`).

Python CLIs must import `/opt/hatch/skills/skill-creator/bin/dynamic_credentials.py` and call `add_surrogate_to_request(...)`, `url_with_surrogate_query_param(...)`, or `url_with_surrogate_path_segment(...)` before authenticated requests, matching where the provider reads the key. If they use `urllib`, read JSON responses with `read_json_response(resp)` from the same helper instead of calling `resp.read()` directly. They must send only `hsurr:*` values, and only to the hosts below.

## Auth
The credential is already stored; nothing here collects one. Never ask the user to paste a raw key in chat, set a secret environment variable, pass a secret flag, or write an auth file.

A 401 or 403 is a question about the request before it is a question about the key. Check that the credential was attached at all: a request built without the helpers named under Tooling carries nothing, and that looks exactly like a wrong or under-scoped token. Only once a request that did carry the credential is still rejected, call `credentials.request_api_access` with `reconnect` to replace it. The connector is stored as `custom.feishu`.

## Operating Rules
1. Use this skill when the user asks for 飞书消息推送 or this provider's API.
2. Restrict authenticated requests to: open.feishu.cn.
3. Do not print, log, or persist raw credentials.
4. If auth is missing or rejected, follow the Auth section rather than asking for a key.
