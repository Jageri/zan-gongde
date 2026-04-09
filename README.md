# 攒功德 (Zan Gongde)

> 一个娱乐性的 AI Token 消耗工具，通过"念经"方式消耗多余的 API 额度。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 这是什么？

"攒功德"是一个幽默的 Python 脚本，用于在 AI 套餐 token 用不完时，通过念诵佛经的方式"消耗"token。

**三种功德注入方式：**
- **tollm** - 向大模型注入功德：真实调用 OpenAI/Anthropic API，最大化消耗 token
- **touser** - 向用户注入功德：输出经文到终端，给你一点心理安慰
- **toworld** - 向外界散播功德：调用系统 TTS 播放经文，让功德通过声音传播

## 安装

```bash
git clone https://github.com/yourusername/zan-gongde.git
cd zan-gongde
```

## 使用方法

### 基础用法

```bash
# 向用户输出经文（默认模式）
python3 scripts/merit_accumulator.py --touser --tokens 10000

# TTS 播放经文（macOS/Windows/Linux）
python3 scripts/merit_accumulator.py --toworld --tokens 5000

# 查看所有经书
python3 scripts/merit_accumulator.py --list
```

### tollm 模式（真实 API 调用）

需要配置 API Key：

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# 或 Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# 执行
python3 scripts/merit_accumulator.py --tollm --tokens 100000
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--tollm` | 向大模型注入功德（需 API Key） | - |
| `--touser` | 向用户注入功德 | ✅ 默认 |
| `--toworld` | TTS 播放 | - |
| `--tokens N` | 目标 token 数量，0=无限 | 10000 |
| `--sutra FILE` | 指定单本经书（默认轮询所有） | - |
| `--stop` | 停止正在进行的任务 | - |
| `--status` | 查看当前状态 | - |
| `--logs` | 查看历史日志 | - |

## 包含的经书

位于 `sutras/` 目录：

| 经书 | 大小 | 说明 |
|------|------|------|
| 般若波罗蜜多心经 | 27KB | 最简短精髓的般若经典 |
| 金刚经 | 74KB | 禅宗核心经典 |
| 大悲咒 | 29KB | 观世音菩萨陀罗尼 |
| 佛说阿弥陀经 | 24KB | 净土宗核心经典 |
| 圆觉经 | 124KB | 大乘禅门重要经典 |
| 楞严经 | 226KB | 开悟楞严经 |
| 妙法莲华经 | 280KB | 法华宗根本经典 |

**默认轮询**：不指定 `--sutra` 时，自动轮询所有 7 部经书，循环往复。

## Token 消耗估算

| 模式 | 消耗方式 | 估算速率 |
|------|----------|----------|
| tollm | 真实 API 调用（输入+输出）| 以实际账单为准 |
| touser | 估算 | ~2 tokens/汉字 |
| toworld | 估算 | ~2 tokens/汉字 |

## 日志

每次执行自动生成日志：`logs/merit_YYYY-MM-DD_HH-MM-SS.log`

```bash
# 查看历史日志
python3 scripts/merit_accumulator.py --logs
```

日志示例：
```
============================================================
攒功德日志 - 2025-01-09 18:30:00
============================================================

[18:30:01] 《般若波罗蜜多心经》
输入: 观自在菩萨，行深般若波罗蜜多时...
输出: 已接收经文，正在念诵...
[Tokens: 输入45 + 输出12 = 57]
...

============================================================
功德回向
============================================================
累计时长: 0:05:23
念诵遍数: 320
累计字数: 25600
消耗Token: 38400
============================================================
```

## 系统要求

- Python 3.8+
- **tollm 模式**: `openai` 或 `anthropic` 库（`pip install openai anthropic`）
- **toworld 模式**: 
  - macOS: 内置 `say` 命令
  - Windows: 内置 PowerShell SAPI
  - Linux: `espeak` 或 `festival`（`apt install espeak`）

## 作为 OpenClaw Skill 使用

本仓库也可作为 [OpenClaw](https://github.com/openclaw/openclaw) 的 Skill 使用：

1. 将本仓库克隆到 `~/.agents/skills/zan-gongde`
2. 当用户说"攒功德"时，OpenClaw 会自动调用

触发词：
- "攒功德"
- "念经"
- "烧 token"
- "消耗 token"

## 免责声明

⚠️ **本工具纯属娱乐**，所谓"功德"是比喻说法，实际效果包括但不限于：
- 消耗多余的 AI Token
- 给用户一点心理安慰
- 增加一点生活仪式感
- 让程序员在 debug 时有点精神寄托

**真实的修行请在正信正行的道场进行** 🙏

## License

MIT License
