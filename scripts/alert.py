#!/usr/bin/env python3
"""探测健康度判定（供 CI 告警步骤使用）。零依赖。

用法：python3 scripts/alert.py [--file data/results.json]
输出一行：healthy / degraded / empty；退出码恒为 0（由 workflow 读取输出决定是否告警）。

判定口径：只看"已配置密钥、真正发过探测"的渠道。
  - 其中至少一个 ok / anon_ok / rate_limited → healthy
  - 全部都不可用 → degraded（疑似网络/平台/密钥整体问题，值得告警）
  - 没有任何已探测渠道（全 no_key / no_probe / retired）→ empty（不告警）
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBED = {"ok", "anon_ok", "rate_limited", "quota_out",
          "auth_invalid", "bad_model", "down"}
ALIVE = {"ok", "anon_ok", "rate_limited"}


def classify(results):
    probed = [r for r in results if r.get("state") in PROBED]
    if not probed:
        return "empty"
    return "healthy" if any(r["state"] in ALIVE for r in probed) else "degraded"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(ROOT / "data" / "results.json"))
    args = ap.parse_args()
    data = json.loads(Path(args.file).read_text())
    print(classify(data["results"]))


if __name__ == "__main__":
    main()
