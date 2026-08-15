#!/usr/bin/env python3
"""
ai-hardware-daily — 每日「新」智能硬件项目抓取

聚焦：最近 N 天「新建」的、与物理硬件 + AI/智能 沾边的 GitHub 仓库。
不是按总 star 排名的老牌大项目，而是刚冒头的新硬件项目。

由 GitHub Actions 每天定时触发。
"""

import requests
import datetime
import os
import sys
from collections import defaultdict

# === 配置 ===
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "daily")

# 只看过去 N 天新建的仓库
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7"))

# 每类最多返回多少个（用于 top 筛选）
PER_QUERY = int(os.environ.get("PER_QUERY", "10"))

# 聚焦「真·智能硬件」的关键词组（每组 ≤5 个 OR 操作符，GitHub Search 硬限制）
# 分类覆盖：机器人 / 嵌入式开发板 / 消费级智能硬件 / 传感器 / 无人机 / 智能家居 / 可穿戴 / AI 边缘
SEARCH_QUERIES = [
    # 机器人 / 具身智能
    ("Robot / Embodied", "robot OR quadruped OR humanoid OR ros2 OR embodied"),
    # 嵌入式 / 单片机开发（拆两条）
    ("Embedded / MCU", "esp32 OR stm32 OR arduino OR rp2040 OR nrf52"),
    ("MCU / Firmware", "microcontroller firmware OR embedded system OR mcu firmware OR realtime embedded"),
    # 消费级智能硬件
    ("Consumer HW", "smart speaker OR wearable OR smart watch OR e-ink OR desk gadget"),
    # 智能家居
    ("Smart Home", "smart home OR home automation OR esphome OR tasmota OR home assistant"),
    # 开源 PCB / 硬件设计（收紧，避免 design 语义漂移）
    ("PCB / KiCad", "kicad OR gerber OR altium library OR pcb design OR open hardware"),
    # 传感器 / 感知
    ("Sensor / Perception", "imu OR lidar OR sensor fusion OR mmwave OR tof sensor"),
    # 无人机 / 运动控制
    ("Drone / Motion", "drone OR uav OR flight controller OR stepper motor OR gimbal"),
    # 边缘 AI 推理
    ("Edge AI", "tinyml OR npu OR edge ai OR ai accelerator OR on-device inference"),
    # RISC-V / FPGA / 定制芯片
    ("RISC-V / FPGA", "risc-v OR fpga OR verilog OR chisel OR custom soc"),
    # IoT 连接 / 网关
    ("IoT / Gateway", "zigbee OR mqtt OR matter protocol OR iot gateway OR lorawan"),
    # 3D 打印 / 硬件外壳 / 自造
    ("Fabrication", "3d print OR enclosure design OR cnc machining OR open source gadget"),
]

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def search_new_repos(query: str, created_after: str, per_page: int) -> list:
    """搜索「最近新建」且与硬件相关的仓库，按 star 排序"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"({query}) created:>{created_after}",
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("items", [])
        elif resp.status_code == 403:
            print(f"  ⚠️ 403 限流: {resp.text[:120]}")
        elif resp.status_code == 401:
            print(f"  ⚠️ 401 token 无效")
        else:
            print(f"  ⚠️ API error {resp.status_code}: {resp.text[:100]}")
        return []
    except Exception as e:
        print(f"  ⚠️ Request error: {e}")
        return []


def fmt_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d")
    except Exception:
        return "?"


def generate_report(results: dict, date_str: str, created_after: str) -> str:
    lines = []
    lines.append(f"# 🤖🔧 每日新智能硬件 — {date_str}")
    lines.append("")
    lines.append(f"> 聚焦「最近新建」的硬件项目 · 只看 {LOOKBACK_DAYS} 天内新建 · 每日 09:00 UTC")
    lines.append("")
    lines.append("---")
    lines.append("")

    seen = set()
    total = 0
    for category, repos in results.items():
        lines.append(f"## 📂 {category}")
        lines.append("")
        if not repos:
            lines.append("*本类近 7 天无新硬件仓库*")
            lines.append("")
            continue
        lines.append("| ⭐ | 仓库 | 新建 | 描述 | 语言 |")
        lines.append("|---|------|------|------|------|")
        for r in repos:
            full = r.get("full_name", "?")
            if full in seen:
                continue
            seen.add(full)
            total += 1
            stars = r.get("stargazers_count", 0)
            name = f"[{full}]({r.get('html_url','#')})"
            created = fmt_date(r.get("created_at", ""))
            desc = (r.get("description") or "—").replace("|", "\\|")[:70]
            lang = r.get("language") or "—"
            lines.append(f"| {stars} | {name} | {created} | {desc} | {lang} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"📊 本日共收录 **{total}** 个新硬件仓库（{LOOKBACK_DAYS} 天内新建，去重后）")
    lines.append("")
    lines.append("*由 [ai-hardware-daily](https://github.com/libiao83/ai-hardware-daily) 自动生成*")
    lines.append("")
    return "\n".join(lines)


def update_index(date_str: str):
    index_path = os.path.join(OUTPUT_DIR, "README.md")
    link = f"- [{date_str}]({date_str}.md)"
    existing = []
    if os.path.exists(index_path):
        with open(index_path) as f:
            existing = f.read().strip().split("\n")
    if link not in existing:
        existing.append(link)
    with open(index_path, "w") as f:
        f.write("\n".join(existing) + "\n")


def main():
    now = datetime.datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    created_after = (now - datetime.timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    print(f"🚀 ai-hardware-daily — {date_str}")
    print(f"👀 只看 {created_after} 之后新建的仓库")
    print("=" * 50)

    results = {}
    for category, query in SEARCH_QUERIES:
        print(f"🔍 {category}...")
        repos = search_new_repos(query, created_after, PER_QUERY)
        results[category] = repos
        print(f"   ✅ {len(repos)} 个")

    report = generate_report(results, date_str, created_after)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{date_str}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    update_index(date_str)

    print(f"\n✅ 日报生成: {output_path} ({len(report)} 字符)")


if __name__ == "__main__":
    main()
