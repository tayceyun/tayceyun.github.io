from __future__ import annotations

import os

import requests


def send_wxpusher(content: str, summary: str, api_url: str, dry_run: bool = False) -> None:
    if dry_run:
        return

    app_token = os.getenv("WXPUSHER_APP_TOKEN")
    uid = os.getenv("WXPUSHER_UID")
    if not app_token or not uid:
        print("未配置 WXPUSHER_APP_TOKEN 或 WXPUSHER_UID，跳过推送")
        return

    response = requests.post(
        api_url,
        json={
            "appToken": app_token,
            "content": content,
            "summary": summary[:100],
            "contentType": 1,
            "uids": [uid],
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 1000:
        raise RuntimeError(f"WxPusher 推送失败: {payload}")
