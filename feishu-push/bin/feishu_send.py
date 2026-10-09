#!/usr/bin/env python3
"""Send a text message to a Feishu group chat via the stored custom.feishu connector.

Auth flow: the App Secret lives in the Secure Vault under connector
``custom.feishu``. This CLI fetches an ``hsurr:*`` surrogate from authd and
appends it as the ``app_secret`` query parameter on Feishu's
tenant_access_token endpoint (Feishu accepts app_id/app_secret as query
params), exchanges it for a short-lived tenant_access_token, then POSTs the
message. Only surrogates are ever sent; Sentinel swaps them for the real
credential on egress to open.feishu.cn. The app_id is a public identifier.
"""

import argparse
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
import dynamic_credentials as dc

APP_ID = "cli_a91f29a06538dbd3"
ALLOWED_HOSTS = ["open.feishu.cn"]
CREDENTIAL_NAME = "custom.feishu"

# Default target: the user's "每日新闻" group (resolved 2026-09-30).
DEFAULT_CHAT_ID = "oc_de457d893dbbe148335a2bf8508da50a"


def get_tenant_token() -> str:
    base = (
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        f"?app_id={APP_ID}"
    )
    url = dc.url_with_surrogate_query_param(
        base, CREDENTIAL_NAME, allowed_hosts=ALLOWED_HOSTS
    )
    req = urllib.request.Request(
        url,
        data=b"{}",
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = dc.read_json_response(resp)
    if data.get("code") != 0:
        raise RuntimeError(f"token exchange failed: {data}")
    return data["tenant_access_token"]


def send_message(chat_id: str, text: str) -> str:
    token = get_tenant_token()
    payload = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = dc.read_json_response(resp)
    if data.get("code") != 0:
        raise RuntimeError(f"send failed: {data}")
    return data["data"]["message_id"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Send a text message to a Feishu group chat.")
    ap.add_argument("--chat-id", default=DEFAULT_CHAT_ID, help="Target chat_id")
    ap.add_argument("--text", required=True, help="Message text")
    args = ap.parse_args()
    message_id = send_message(args.chat_id, args.text)
    print(json.dumps({"ok": True, "message_id": message_id}, ensure_ascii=False))


if __name__ == "__main__":
    main()
