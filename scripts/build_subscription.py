#!/usr/bin/env python3
"""Build a plain-text TURN subscription from the upstream CSV."""
import csv
import io
import urllib.request
from pathlib import Path

SOURCE = "https://raw.githubusercontent.com/lc69282940/gh-turnrank/main/rank/rank-latest.csv"
PREFIX = "ovo.miumiumiu.cc.cd:443"
NAME = "链式TURN代理"
OUTPUT = Path("subscribe.txt")

def find_key(headers, candidates):
    lowered = {h.strip().lower(): h for h in headers}
    for candidate in candidates:
        if candidate.lower() in lowered:
            return lowered[candidate.lower()]
    for candidate in candidates:
        for header in headers:
            if candidate.lower() in header.strip().lower():
                return header
    return None

request = urllib.request.Request(SOURCE, headers={"User-Agent": "turn-subscription-builder"})
with urllib.request.urlopen(request, timeout=30) as response:
    raw = response.read().decode("utf-8-sig")

reader = csv.DictReader(io.StringIO(raw))
headers = reader.fieldnames or []
relay_key = find_key(headers, ["中继", "relay", "turn", "地址", "server"])
country_key = find_key(headers, ["国家", "country", "地区", "国家代码"])
status_key = find_key(headers, ["判定", "状态", "status", "result"])
if not relay_key or not country_key:
    raise SystemExit("CSV 缺少中继地址列或国家列：" + ", ".join(headers))

lines = []
for row in reader:
    relay = (row.get(relay_key) or "").strip()
    country = (row.get(country_key) or "").strip()
    status = (row.get(status_key) or "").strip() if status_key else ""
    if not relay or not country or (status_key and status != "正常"):
        continue
    if not relay.lower().startswith("turn://"):
        relay = "turn://" + relay
    lines.append(f"{PREFIX}#{country} {NAME}${relay}")

if not lines:
    raise SystemExit("没有生成任何正常节点；为避免覆盖有效订阅，停止更新。")

OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Generated {len(lines)} TURN nodes.")
