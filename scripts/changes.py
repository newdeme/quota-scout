#!/usr/bin/env python3
"""生成某时间窗内的渠道变更简报（Markdown）。零依赖，输出确定性。

事件类型：
  1. 状态迁移   —— 来自 data/history.jsonl（窗口起点前最后状态 vs 窗口末最后状态）
  2. 渠道增删   —— 来自 git 中窗口起/止两个时间点的 data/channels.json
  3. 额度文案变更 —— 同上，比较 free_tier / free_tier_en
需要 git 历史（CI 请用 fetch-depth: 0）；取不到历史时第 2、3 类降级并注明。

用法：python3 scripts/changes.py --since 2026-10-01 --until 2026-11-01
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALIVE = {"ok", "anon_ok", "rate_limited"}


def load_history():
    rows = []
    for line in (ROOT / "data" / "history.jsonl").read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def last_state(rows, upto):
    """每渠道在 ts<upto（ISO 字符串比较）之前的最后一条状态。"""
    out = {}
    for r in rows:
        if r["ts"] < upto:
            out[r["id"]] = r["state"]
    return out


def channels_at(spec):
    """spec 为 YYYY-MM-DD（取该日 00:00Z 前最后一次提交）或任意 git rev；取不到返回 None。"""
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", spec):
            rev = subprocess.run(
                ["git", "rev-list", "-1", f"--before={spec}T00:00:00Z", "HEAD"],
                cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        else:
            rev = spec
        if not rev:
            return None
        raw = subprocess.run(
            ["git", "show", f"{rev}:data/channels.json"],
            cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return {c["id"]: c for c in json.loads(raw)["channels"]}
    except (subprocess.CalledProcessError, FileNotFoundError, KeyError):
        return None


def build(since, until, from_rev=None, to_rev=None):
    rows = load_history()
    before = last_state(rows, since)
    after = last_state(rows, until)
    names = {}
    cur = {c["id"]: c for c in json.loads(
        (ROOT / "data" / "channels.json").read_text())["channels"]}
    for k, v in cur.items():
        names[k] = v["name"]

    transitions = [(k, before[k], after[k]) for k in sorted(after)
                   if k in before and before[k] != after[k]]
    appeared = [k for k in sorted(after) if k not in before]

    old, new = channels_at(from_rev or since), channels_at(to_rev or until)
    added = removed = changed = None
    if old is not None and new is not None:
        added = sorted(set(new) - set(old))
        removed = sorted(set(old) - set(new))
        changed = [k for k in sorted(set(new) & set(old))
                   if (old[k].get("free_tier_en"), old[k].get("free_tier")) !=
                   (new[k].get("free_tier_en"), new[k].get("free_tier"))]
        for k in set(new) | set(old):
            names.setdefault(k, (new.get(k) or old.get(k))["name"])

    n_alive = sum(1 for s in after.values() if s in ALIVE)
    lines = [f"## Radar digest {since} → {until}", "",
             f"{n_alive}/{len(after)} channels alive at window end.", ""]
    ev = 0

    def section(title, items):
        nonlocal ev
        if items:
            lines.append(f"### {title}")
            lines.extend(items)
            lines.append("")
            ev += len(items)

    section("Channels added", [f"- {names[k]} (`{k}`)" for k in (added or [])])
    section("Channels removed", [f"- {names.get(k, k)} (`{k}`)" for k in (removed or [])])
    section("Status changes",
            [f"- {names[k]} (`{k}`): `{a}` → `{b}`" for k, a, b in transitions])
    section("Free-tier wording changed",
            [f"- {names[k]} (`{k}`)" for k in (changed or [])])
    section("First probed in this window",
            [f"- {names.get(k, k)} (`{k}`): `{after[k]}`" for k in appeared])
    if ev == 0:
        lines += ["No channel changes in this window.", ""]
    if added is None:
        lines += ["_(git history unavailable: channel add/remove and wording "
                  "changes were not evaluated.)_", ""]
    return "\n".join(lines).rstrip() + "\n", ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="YYYY-MM-DD（含）")
    ap.add_argument("--until", required=True, help="YYYY-MM-DD（不含）")
    ap.add_argument("--from-rev", help="渠道清单对比起点（git rev；默认取 --since 当日）")
    ap.add_argument("--to-rev", help="渠道清单对比终点（git rev；默认取 --until 当日）")
    args = ap.parse_args()
    text, _ = build(args.since, args.until, args.from_rev, args.to_rev)
    print(text, end="")


if __name__ == "__main__":
    main()
