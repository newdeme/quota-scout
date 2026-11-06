#!/usr/bin/env python3
"""把 data/results.json 渲染进双语 README（EN 默认 + zh-CN 配套），生成 assets/radar.svg 与徽章 JSON。零依赖。"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START, END = "<!-- RADAR:START -->", "<!-- RADAR:END -->"

ICON = {"ok": "✅", "anon_ok": "🟢", "rate_limited": "🟡", "no_key": "⚪",
        "auth_invalid": "🔑", "bad_model": "🏷️", "quota_out": "💸",
        "down": "❌", "retired": "🪦", "no_probe": "📖"}

STATE_CN = {"ok": "验证可用", "anon_ok": "匿名可用", "rate_limited": "限流(服务正常)",
            "no_key": "待密钥", "auth_invalid": "密钥无效", "bad_model": "模型待更新",
            "quota_out": "额度耗尽", "down": "不可用", "retired": "官方退役",
            "no_probe": "收录未探测"}
STATE_EN = {"ok": "verified", "anon_ok": "anon OK", "rate_limited": "rate-limited (alive)",
            "no_key": "awaiting key", "auth_invalid": "key rejected", "bad_model": "stale model",
            "quota_out": "quota spent", "down": "down", "retired": "RETIRED",
            "no_probe": "doc-only"}

HEAD_CN = ("| 渠道 | 网络 | 免费方式（快照，以官方为准） | 状态 | 延迟 "
           "| 最后验证可用 (UTC) | 密钥变量 | 注册 |\n"
           "|---|---|---|---|---|---|---|---|")
HEAD_EN = ("| Channel | Network | Free tier (snapshot; official pages win) | Status | Latency "
           "| Last verified OK (UTC) | Key var | Sign up |\n"
           "|---|---|---|---|---|---|---|---|")

SECTIONS = {
    "zh": [("### 🇨🇳 国内额度 · 大陆直连优先", "cn"),
           ("### 🌍 国际额度 · 多数需国际网络", "intl")],
    "en": [("### 🇨🇳 China-direct · works from mainland networks", "cn"),
           ("### 🌍 Global · usually needs international networking", "intl")],
}
NET = {"zh": {"direct": "`直连✓`", "intl": "`需国际网络`"},
       "en": {"direct": "`direct ✓`", "intl": "`intl net`"}}
TIER_KEY = {"zh": "free_tier", "en": "free_tier_en"}
SIGNUP = {"zh": "注册", "en": "Sign up"}

conf = json.loads((ROOT / "data" / "channels.json").read_text())
results = {r["id"]: r for r in json.loads(
    (ROOT / "data" / "results.json").read_text())["results"]}


def last_verified():
    """每渠道最近一次 ok/anon_ok 的时间戳（来自 history.jsonl，再并入本轮结果）。"""
    out = {}
    hist = ROOT / "data" / "history.jsonl"
    for line in hist.read_text().splitlines() if hist.exists() else []:
        if line.strip():
            e = json.loads(line)
            if e.get("state") in ("ok", "anon_ok"):
                out[e["id"]] = max(out.get(e["id"], ""), e["ts"])
    for k, r in results.items():
        if r.get("state") in ("ok", "anon_ok"):
            out[k] = max(out.get(k, ""), r["ts"])
    return out


VERIFIED = last_verified()
groups = {"cn": [c for c in conf["channels"] if c["cn_access"] == "direct"],
          "intl": [c for c in conf["channels"] if c["cn_access"] == "intl"]}


def row(ch: dict, lang: str) -> str:
    r = results.get(ch["id"], {})
    state = r.get("state", "down")
    lat = r.get("latency_ms")
    labels = STATE_CN if lang == "zh" else STATE_EN
    dagger = "†" if ch.get("bonus_once") else ""
    tier = ch[TIER_KEY[lang]] + dagger
    name = ch.get('name_en', ch['name']) if lang == 'en' else ch['name']
    return (f"| [{name}]({ch['home']}) | {NET[lang][ch['cn_access']]} | {tier} "
            f"| {ICON[state]} {labels[state]} "
            f"| {str(lat)+' ms' if lat else '—'} "
            f"| {VERIFIED.get(ch['id'], '—')} "
            f"| `{ch.get('key_env') or '—'}` | [{SIGNUP[lang]}]({ch['key_signup']}) |")


def build_table(lang: str) -> str:
    head = HEAD_CN if lang == "zh" else HEAD_EN
    return "\n\n".join(
        title + "\n\n" + head + "\n" + "\n".join(row(c, lang) for c in groups[gkey])
        for title, gkey in SECTIONS[lang] if groups[gkey])


import re
def cjk_guard(text, allow):
    bad = {m for m in re.findall(r'[\u4e00-\u9fff]+', text)} - allow
    assert not bad, f"EN README CJK leak: {bad}"

for path, lang in ((ROOT / "README.md", "en"),
                   (ROOT / "README.zh-CN.md", "zh")):
    text = path.read_text()
    assert START in text and END in text, f"{path.name} 缺少 RADAR 标记区间"
    head, _, rest = text.partition(START)
    _, _, tail = rest.partition(END)
    out = head + START + "\n" + build_table(lang) + "\n" + END + tail
    if lang == "en":
        cjk_guard(out, {"简体中文"})
    path.write_text(out)

# ---------- 动态徽章 ----------
ok_n = sum(1 for e in results.values() if e["state"] in ("ok", "anon_ok"))
usable = sum(1 for e in results.values()
             if e["state"] in ("ok", "anon_ok", "rate_limited"))
total = len(conf["channels"])
gen_at = next(iter(results.values()), {}).get("ts", "—")
badges = {
    "alive": {"schemaVersion": 1, "label": "scout sweep",
              "message": f"{usable}/{total} alive",
              "color": "brightgreen" if ok_n else ("yellow" if usable else "red")},
    "sweep": {"schemaVersion": 1, "label": "last sweep",
              "message": gen_at.replace("T", " ")[:17] + " UTC", "color": "blue"},
}
for k, v in badges.items():
    (ROOT / "data" / f"badge-{k}.json").write_text(
        json.dumps(v, ensure_ascii=False) + "\n")

# ---------- 雷达 SVG ----------
C = {"retired": "#94A3B8", "ok": "#22C55E", "anon_ok": "#4ADE80", "rate_limited": "#FBBF24",
     "auth_invalid": "#94A3B8", "no_key": "#CBD5E1", "bad_model": "#F97316",
     "quota_out": "#FB7185", "down": "#F87171", "no_probe": "#E2E8F0"}
SIZE, R = 440, 178
CX = CY = SIZE / 2


def blip(ch, idx, n):
    ang = -90 + idx * 360 / n
    r = results.get(ch["id"], {})
    state, lat = r.get("state", "down"), r.get("latency_ms")
    if lat is None:
        dist, hole = 0.18 * R, True
    elif lat < 800:
        dist, hole = 0.36 * R, False
    elif lat < 2000:
        dist, hole = 0.63 * R, False
    else:
        dist, hole = 0.9 * R, False
    x = CX + dist * math.cos(math.radians(ang))
    y = CY + dist * math.sin(math.radians(ang))
    col = C[state]
    parts = [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{col}" '
             f'fill-opacity="{0.25 if hole else 1}" stroke="{col}" stroke-width="2"/>']
    # 国内=菱形外框；国际=纯圆 —— 形状区分分组，不引入第二色相
    if ch["cn_access"] == "direct":
        parts.append(f'<rect x="-6" y="-6" width="12" height="12" transform='
                     f'"translate({x:.1f},{y:.1f}) rotate(45)" fill="none" '
                     f'stroke="{col}" stroke-width="1.6"/>')
    return "".join(parts)


ordered = groups["cn"] + groups["intl"]
n = len(ordered)
sweep_deg = 42
sweep_end_x = CX + R * math.cos(math.radians(-90 + sweep_deg))
sweep_end_y = CY + R * math.sin(math.radians(-90 + sweep_deg))
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" '
       f'viewBox="0 0 {SIZE} {SIZE}">']
svg.append(f'<path d="M{CX},{CY} L{CX},{CY - R} A{R},{R} 0 0 1 '
           f'{sweep_end_x:.1f},{sweep_end_y:.1f} Z" fill="#22C55E" fill-opacity="0.06"/>'
           f'<line x1="{CX}" y1="{CY}" x2="{CX}" y2="{CY - R}" '
           f'stroke="#22C55E" stroke-opacity="0.55" stroke-width="1.5"/>')
for frac in (0.33, 0.66, 1.0):
    svg.append(f'<circle cx="{CX}" cy="{CY}" r="{R * frac:.0f}" fill="none" '
               f'stroke="#64748B" stroke-opacity="0.30"/>')
svg.append(f'<line x1="{CX - R}" y1="{CY}" x2="{CX + R}" y2="{CY}" '
           f'stroke="#64748B" stroke-opacity="0.15"/>')
svg.append(f'<line x1="{CX}" y1="{CY - R}" x2="{CX}" y2="{CY + R}" '
           f'stroke="#64748B" stroke-opacity="0.15"/>')
svg.extend(blip(ch, i, n) for i, ch in enumerate(ordered))
svg.append(f'<text x="{CX}" y="{CY - 8}" text-anchor="middle" '
           f'font-family="ui-monospace,Menlo,monospace" font-size="13" '
           f'letter-spacing="3" fill="#94A3B8">QUOTA·SCOUT</text>')
svg.append(f'<text x="{CX}" y="{CY + 14}" text-anchor="middle" font-family="sans-serif" '
           f'font-size="11" fill="#64748B">{usable}/{total} alive · {gen_at[:10]}</text>')
svg.append("</svg>")
assets = ROOT / "assets"
assets.mkdir(exist_ok=True)
(assets / "radar.svg").write_text("\n".join(svg) + "\n")

print(f"README.md(EN) + README.zh-CN.md 已更新；radar.svg / badge-*.json 已生成"
      f"（可用 {usable}/{total}）")
