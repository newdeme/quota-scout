#!/usr/bin/env python3
"""月度简报：生成上月变更简报，写入 CHANGELOG（幂等），并输出 Release 说明文件。零依赖。

用法：
  python3 scripts/digest.py                 # 默认：今天所在月的"上一个月"
  python3 scripts/digest.py --month 2026-10 # 指定月份
  --notes-file PATH                         # Release 说明输出位置（默认 /tmp/radar-digest.md）
  --dry-run                                 # 只打印，不改 CHANGELOG
stdout 最后一行：month=YYYY-MM changed=<0|1>（已存在则 changed=0，供 workflow 判断是否提交）
"""
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import changes  # noqa: E402

ROOT = changes.ROOT
MARK = "<!-- DIGEST:START -->"


def month_window(month):
    y, m = map(int, month.split("-"))
    ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{y:04d}-{m:02d}-01", f"{ny:04d}-{nm:02d}-01"


def prev_month(today):
    y, m = today.year, today.month
    return f"{y - 1:04d}-12" if m == 1 else f"{y:04d}-{m - 1:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month")
    ap.add_argument("--notes-file", default="/tmp/radar-digest.md")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    month = args.month or prev_month(date.today())
    since, until = month_window(month)
    text, _ = changes.build(since, until)
    # CHANGELOG 里把二级标题降为三级，并带上月份标识，便于幂等检查
    entry = text.replace("## Radar digest", f"## [radar-{month}] Radar digest", 1)
    Path(args.notes_file).write_text(text)
    print(entry)

    cl = ROOT / "CHANGELOG.md"
    body = cl.read_text()
    changed = 0
    if f"[radar-{month}]" not in body and not args.dry_run:
        if MARK in body:
            body = body.replace(MARK, MARK + "\n\n" + entry.rstrip() + "\n", 1)
        else:  # 首次：在首个标题后建立标记区
            head, _, rest = body.partition("\n")
            body = f"{head}\n\n{MARK}\n\n{entry.rstrip()}\n\n<!-- DIGEST:END -->\n{rest}"
        cl.write_text(body)
        changed = 1
    print(f"month={month} changed={changed}")


if __name__ == "__main__":
    main()
