#!/usr/bin/env python3
"""额度雷达探活脚本。零第三方依赖（仅标准库）。

状态定义：
  ok            已配置密钥且调用成功
  anon_ok       未配密钥但匿名调用成功（渠道声明支持匿名）
  rate_limited  收到 429 —— 服务本身可用，只是限流（视为半可用）
  auth_invalid  密钥存在但被拒（401/403）
  no_key        未配置密钥且渠道不支持匿名 —— 跳过探测
  bad_model     服务可达但模型 ID 无效/下架（404 或模型类错误）
  quota_out     额度耗尽（402 类）
  down          网络失败 / 5xx / 其他异常
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

STATE_ORDER = ["ok", "anon_ok", "rate_limited", "no_key", "auth_invalid",
               "bad_model", "quota_out", "down", "retired"]
ICON = {"ok": "✅", "anon_ok": "🟢", "rate_limited": "🟡", "no_key": "⚪",
        "auth_invalid": "🔑", "bad_model": "🏷️", "quota_out": "💸",
        "down": "❌", "retired": "🪦"}


def load_env_file(path: Path) -> dict:
    env = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip("'\"")
    return env


def probe_openai_chat(ch: dict, keys: dict, timeout_s: int) -> dict:
    p = ch["probe"]
    key = keys.get(ch.get("key_env") or "", "")
    # 部分 API（如 Groq）在 Cloudflare 后按客户端签名封禁默认 Python-UA → error 1010
    headers = {"Content-Type": "application/json",
               "User-Agent": "quota-scout/0.2 (+github.com/newdeme/quota-scout)"}
    has_key = bool(key)
    if has_key:
        headers["Authorization"] = f"Bearer {key}"
    elif not ch.get("anonymous"):
        return {"state": "no_key", "detail": f"未配置 {ch['key_env']}"}

    body = json.dumps({
        "model": p["model"],
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": p.get("max_tokens", 8),
    }).encode()

    req = urllib.request.Request(p["base_url"], data=body, headers=headers)
    t0 = time.monotonic()
    try:
        for attempt in range(2):  # 网络抖动重试一次；HTTPError 直接抛给外层分类
            try:
                with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                    resp.read()
                    latency = int((time.monotonic() - t0) * 1000)
                    state = "ok" if has_key else "anon_ok"
                    return {"state": state, "latency_ms": latency,
                            "detail": f"HTTP {resp.status}"}
            except urllib.error.HTTPError:
                raise
            except Exception:
                if attempt == 0:
                    time.sleep(2)
                else:
                    raise
    except urllib.error.HTTPError as e:
        latency = int((time.monotonic() - t0) * 1000)
        detail = f"HTTP {e.code}"
        try:
            snippet = e.read().decode("utf-8", "replace")[:180]
        except Exception:
            snippet = ""
        if e.code == 429:
            return {"state": "rate_limited", "latency_ms": latency,
                    "detail": "429 限流（服务正常）"}
        if e.code in (401, 403):
            return {"state": "auth_invalid", "latency_ms": latency,
                    "detail": f"{detail} 密钥被拒"}
        if e.code in (402,):
            return {"state": "quota_out", "latency_ms": latency,
                    "detail": "402 额度不足"}
        if e.code == 410 or "retir" in snippet.lower():
            return {"state": "retired", "latency_ms": latency,
                    "detail": f"{detail} 官方退役/brownout"}
        if e.code == 404 or "model" in snippet.lower():
            return {"state": "bad_model", "latency_ms": latency,
                    "detail": detail}
        return {"state": "down", "latency_ms": latency, "detail": detail}
    except Exception as e:
        latency = int((time.monotonic() - t0) * 1000)
        return {"state": "down", "latency_ms": latency,
                "detail": type(e).__name__}


def main():
    ap = argparse.ArgumentParser(description="free-quota radar prober")
    ap.add_argument("--only", help="逗号分隔的 channel id 列表")
    ap.add_argument("--timeout", type=int, default=45,
                    help="单请求超时秒数（默认 45）")
    ap.add_argument("--env-file", default=str(ROOT / ".env"))
    args = ap.parse_args()

    conf = json.loads((DATA / "channels.json").read_text())
    order = [c["id"] for c in conf["channels"]]
    channels = conf["channels"]
    if args.only:
        want = set(args.only.split(","))
        channels = [c for c in channels if c["id"] in want]

    file_env = load_env_file(Path(args.env_file))
    import os
    keys = dict(file_env)
    keys.update({k: v for k, v in os.environ.items() if v})  # 真 env 优先

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    for ch in channels:
        if not ch.get("probe"):
            r = {"state": "no_probe", "detail": "手册收录（暂无自动探活）"}
        else:
            r = probe_openai_chat(ch, keys, args.timeout)
        entry = {"id": ch["id"], "ts": now, **r}
        results.append(entry)
        print(f"{ICON.get(r['state'], '·')} [{r['state']:>12}] {ch['name']:<28} {r.get('detail','')}")

    # 合并写入：--only 部分探测不得覆盖其余渠道的既有状态
    try:
        prev = {r["id"]: r for r in json.loads(
            (DATA / "results.json").read_text())["results"]}
    except Exception:
        prev = {}
    if args.only:
        have = {e["id"] for e in results}
        results = results + [prev[k] for k in prev if k not in have]
        results.sort(key=lambda e: order.index(e["id"]))
    (DATA / "results.json").write_text(
        json.dumps({"generated_at": now, "results": results},
                   ensure_ascii=False, indent=2) + "\n")

    with open(DATA / "history.jsonl", "a") as f:
        for e in results:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    ok_n = sum(1 for e in results if e["state"] in ("ok", "anon_ok"))
    usable = sum(1 for e in results
                 if e["state"] in ("ok", "anon_ok", "rate_limited"))
    total = len(results)
    # 徽章由 render.py 统一生成（badge-alive / badge-sweep）
    print(f"\n可用 {usable}/{total}（其中实弹验证 {ok_n}），结果已写入 data/")


if __name__ == "__main__":
    sys.exit(main())
