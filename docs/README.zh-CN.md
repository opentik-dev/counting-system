# Warehouse Vision Counting System

**语言：** [العربية](../README.md) · [English](README.en.md) · [Français](README.fr.md) · [Español](README.es.md) · [Türkçe](README.tr.md) · [中文](README.zh-CN.md)

这是一个离线优先、可审计的仓库视觉计数核心，用于统计穿过仓库计数线的
纸箱和托盘。MVP 将跟踪观测转换为带方向的 `IN/OUT` 事件，避免重复计数，
并将证据元数据保存到 SQLite。

## 快速开始

```bash
python3 -m pytest -q
PYTHONPATH=src python3 -m warehouse_counting.demo
```

核心仅需要 Python 3.11+ 和标准库。实时摄像头、仪表板和生产环境精度验证
属于后续路线图；当前视频只是补充训练材料，不是最终验收基准。

## 当前范围

单条计数线、`carton` 和 `pallet` 对象、置信度和类别过滤、重复事件防护、
SQLite 持久化，以及明确的托盘容量规则。

## 加入开发者社区

欢迎开发者、研究人员、仓库运营人员和翻译者参与改进。请阅读
[`CONTRIBUTING.md`](../CONTRIBUTING.md)，提交 Issue，并创建范围清晰、经过
测试的 Pull Request。我们尤其需要真实固定视角视频和人工地面真值数据。

## 许可证

MIT — 参见 [`LICENSE`](../LICENSE)。
