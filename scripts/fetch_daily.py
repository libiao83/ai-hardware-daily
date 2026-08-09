#!/usr/bin/env python3
"""
ai-hardware-daily — 每日 AI 硬件/项目热点抓取

通过 GitHub Search API 抓取当日最热的 AI 硬件相关仓库，
生成 Markdown 日报。由 GitHub Actions 每天定时触发。
"""

import requests
import datetime
import os
import sys
from collections import defaultdict

# === 配置 ===
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "daily")

SEARCH_QUERIES = [
    # AI 芯片/硬件加速
    ("AI Chip / Accelerator", "ai chip OR npu OR tpu OR ai accelerator OR neural engine"),
    # 边缘 AI / TinyML
    ("Edge AI / TinyML", "edge ai OR tinyml OR on-device ml OR embedded ai OR microcontroller ml"),
    # 机器人 / 具身智能
    ("Robotics / Embodied AI", "robot OR embodied ai OR ros2 OR humanoid robot"),
    # 开源硬件 / RISC-V
    ("Open Hardware / RISC-V", "open source hardware OR risc-v ai OR fpga ai OR open pcb"),
    # AI 编译器 / 模型优化
    ("AI Compiler / Optimization", "ml compiler OR model optimization OR onnx OR tvm OR quantization OR llm inference"),
    # 无人机 / 自动驾驶
    ("Drone / Autonomous", "drone OR autonomous vehicle OR ADAS OR flight controller OR lidar slam"),
    # 传感器融合 / 智能感知
    ("Smart Sensor / Perception", "smart sensor OR imu sensor OR sensor fusion OR computer vision hardware"),
    # AI 推理部署
    ("Inference Deployment", "llm deployment OR vllm OR ollama OR local llm OR inference server"),
    # 大模型训练/微调工具
    ("LLM Training / Finetune", "llm finetune OR lora OR qlora OR rlhf OR model training framework"),
    # AI Agent 框架
    ("AI Agent Framework", "ai agent framework OR multi agent OR agent orchestration OR tool calling"),
]

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


def search_repos(query: str, per_page: int = 10) -> list:
    """搜索 GitHub 仓库，按 stars 排序"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"{query} sort:stars",
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    }
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("items", [])
        else:
            print(f"  ⚠️ API error {resp.status_code}: {resp.text[:100]}")
            return []
    except Exception as e:
        print(f"  ⚠️ Request error: {e}")
        return []


def generate_report(all_results: dict, date_str: str) -> str:
    """生成 Markdown 日报"""
    lines = []
    lines.append(f"# 🤖🔧 AI 硬件/项目日报 — {date_str}")
    lines.append("")
    lines.append(f"> 自动抓取 · 每日 09:00 UTC | 覆盖 {len(SEARCH_QUERIES)} 个方向")
    lines.append("")
    lines.append("---")
    lines.append("")

    total_repos = 0

    for category, repos in all_results.items():
        lines.append(f"## 📂 {category}")
        lines.append("")
        if not repos:
            lines.append("*今日无新的高星仓库*")
            lines.append("")
            continue

        lines.append("| ⭐ Stars | 仓库 | 描述 | 语言 |")
        lines.append("|---------|------|------|------|")
        for r in repos[:5]:  # 每类取 top 5
            total_repos += 1
            stars = r.get("stargazers_count", 0)
            name = f"[{r.get('full_name','?')}]({r.get('html_url','#')})"
            desc = (r.get("description") or "—")[:80]
            lang = r.get("language") or "—"
            lines.append(f"| {stars} | {name} | {desc} | {lang} |")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"📊 本日共收录 **{total_repos}** 个热门仓库")
    lines.append("")
    lines.append("*由 [ai-hardware-daily](https://github.com/libiao83/ai-hardware-daily) 自动生成*")
    lines.append("")

    return "\n".join(lines)


def main():
    today = datetime.datetime.utcnow()
    date_str = today.strftime("%Y-%m-%d")

    print(f"🚀 ai-hardware-daily — {date_str}")
    print(f"{'='*50}")

    all_results = {}
    for category, query in SEARCH_QUERIES:
        print(f"🔍 Searching: {category}...")
        repos = search_repos(query)
        all_results[category] = repos
        print(f"   Found {len(repos)} repos")

    # 生成日报
    report = generate_report(all_results, date_str)

    # 写入文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{date_str}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    # 也更新 README 中的索引
    update_index(date_str)

    print(f"\n✅ 日报已生成: {output_path}")
    print(f"📏 文件大小: {len(report)} 字符")


def update_index(date_str: str):
    """更新 daily/README.md 索引导航"""
    index_path = os.path.join(OUTPUT_DIR, "README.md")
    link = f"- [{date_str}]({date_str}.md)"

    existing = []
    if os.path.exists(index_path):
        with open(index_path) as f:
            existing = f.read().strip().split("\n")

    if link not in existing:
        existing.insert(1, link)  # 插到标题后面

    with open(index_path, "w") as f:
        f.write("\n".join(existing) + "\n")


if __name__ == "__main__":
    main()
