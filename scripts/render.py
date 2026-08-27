#!/usr/bin/env python3
"""把 data/results.json 渲染进 README.md 的标记区间。零依赖。"""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START, END = "<!-- RADAR:START -->", "<!-- RADAR:END -->"

ICON = {"ok": "✅", "anon_ok": "🟢", "rate_limited": "🟡", "no_key": "⚪",
        "auth_invalid": "🔑", "bad_model": "🏷️", "quota_out": "💸",
        "down": "❌", "no_probe": "📖"}
STATE_CN = {"ok": "验证可用", "anon_ok": "匿名可用", "rate_limited": "限流(服务正常)",
            "no_key": "待密钥", "auth_invalid": "密钥无效", "bad_model": "模型待更新",
            "quota_out": "额度耗尽", "down": "不可用", "no_probe": "收录未探测"}

readme = ROOT / "README.md"
conf = json.loads((ROOT / "data" / "channels.json").read_text())
results = {r["id"]: r for r in json.loads(
    (ROOT / "data" / "results.json").read_text())["results"]}

cat_cn = {"intl": "国际", "cn": "国内"}
rows = []
for ch in conf["channels"]:
    r = results.get(ch["id"], {})
    state = r.get("state", "down")
    lat = r.get("latency_ms")
    probed = state not in ("no_key",)
    rows.append(
        f"| [{ch['name']}]({ch['home']}) | {cat_cn[ch['category']]} "
        f"| {ch['free_tier']} | {ICON[state]} {STATE_CN[state]} "
        f"| {str(lat)+' ms' if lat else '—'} | {r.get('ts', '—') if probed else '—'} "
        f"| `{ch.get('key_env') or '—'}` | [注册]({ch['key_signup']}) |")

table = (
    "| 渠道 | 分类 | 免费方式（快照，以官方为准） | 状态 | 延迟 | 最后探测 (UTC) | 密钥变量 | 注册 |\n"
    "|---|---|---|---|---|---|---|---|\n"
    + "\n".join(rows))

text = readme.read_text()
assert START in text and END in text, "README 缺少 RADAR 标记区间"
head, _, rest = text.partition(START)
_, _, tail = rest.partition(END)
readme.write_text(head + START + "\n" + table + "\n" + END + tail)
print(f"README 已更新：{len(rows)} 个渠道")
