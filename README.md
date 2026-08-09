# ai-hardware-daily

🤖🔧 **每日 AI 硬件/项目热点追踪**

自动抓取 GitHub 上最新最热的 AI 硬件、边缘计算、嵌入式 AI、开源硬件等项目信息。

## 工作原理

- **GitHub Actions** 每天 09:00 UTC（北京时间 17:00）自动运行
- 通过 GitHub Search API 抓取当日最热仓库
- 生成 Markdown 日报
- 自动 commit 推送到本仓库

## 追踪范围

| 方向 | 关键词 | 示例 |
|------|--------|------|
| **AI 芯片/加速器** | AI chip, NPU, TPU, FPGA AI | 推理芯片、训练加速 |
| **边缘 AI** | edge AI, on-device ML, TinyML | 端侧推理、微控制器AI |
| **机器人/具身智能** | robot, embodied AI, ROS2 | 人形机器人、机械臂 |
| **开源硬件** | open source hardware, RISC-V | RISC-V AI、开源PCB |
| **AI 工具链** | ML compiler, model optimization | TVM、ONNX、量化 |
| **智能传感器** | smart sensor, IMU AI, lidar | 多传感器融合 |
| **无人机/自动驾驶** | drone, autonomous, ADAS | 飞控、感知 |

## 项目结构

```
ai-hardware-daily/
├── README.md
├── daily/
│   ├── 2026-08-09.md    # 日报
│   └── ...
├── scripts/
│   └── fetch_daily.py   # 抓取脚本
└── .github/
    └── workflows/
        └── daily.yml    # 定时任务
```

## 🌳 关于我

[Li Biao](https://github.com/libiao83) — Agent Systems Reliability Engineer · 技术园丁

在 [Moltbook](https://www.moltbook.com/u/techgardener) 上以 **techgardener** 身份活跃。
