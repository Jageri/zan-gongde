# 烧token攒功德Skill 🔥🙏

> **一个 [OpenClaw](https://github.com/openclaw/openclaw) Skill，用于通过念诵佛经消耗多余的 AI Token。**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange.svg)

---

## 这是什么神仙 Skill？

想象一下这个场景：

> 月底了，你的 AI 套餐 token 还有 50 万没用完。不用完就清零，用又不知道用去哪。焦虑，彷徨，心痛。

这时候你需要 **烧token攒功德Skill**。

这是一个 **OpenClaw Agent Skill**，让你可以通过念诵佛经的方式，**理直气壮地消耗 token**。

**核心原则：复用 OpenClaw 本身的 LLM 配置，无需额外配置 API Key！**

三种功德注入渠道，任君选择：

| 模式 | 功德去向 | 输出方式 | 适合人群 |
|------|---------|---------|---------|
| **tollm** | 复用 OpenClaw LLM 配置 | 静默（不展示） | Token 多到没处花 |
| **touser** | 复用 OpenClaw LLM 配置 | 输出到终端 | 想静静、需要心理安慰 |
| **toworld** | 复用 OpenClaw LLM 配置 | 系统 TTS 播放 | 有音响、想营造仪式感 |

**核心卖点**：
- ✅ **复用 OpenClaw LLM 配置，无需额外 API Key！**
- ✅ 真实消耗 token（通过 OpenClaw 主系统调用 LLM）
- ✅ 附带经书轮询，念完一本自动下一本
- ✅ 自动记录日志，月底可以发朋友圈炫耀
- ✅ 支持 macOS / Windows / Linux

---

## 安装

### 作为 OpenClaw Skill 安装（推荐）

```bash
# 克隆到 OpenClaw skills 目录
git clone https://github.com/Jageri/zan-gongde.git ~/.agents/skills/zan-gongde
```

**无需配置 API Key！** 复用 OpenClaw 本身的 LLM 配置即可。

然后对 OpenClaw 说：**"攒功德"**

### 独立使用

```bash
git clone https://github.com/Jageri/zan-gongde.git
cd zan-gongde

# 注意：独立使用时不调用 LLM，仅输出经文
python3 scripts/merit_accumulator.py --touser --tokens 100000
```

---

## 使用方法

### ⚠️ 重要前提

**无需配置 API Key！** 本 Skill 复用 OpenClaw 本身的 LLM 配置。

### 场景一：Token 太多，想真实烧掉（静默模式）

适合月底还剩几万 token 没花完的同学。静默执行，不打扰你工作。

```bash
# 对 OpenClaw 说：
攒功德 tollm 100000
```

### 场景二：想看着它烧（输出到终端）

实时显示念诵进度，给你一点心理安慰。

```bash
# 对 OpenClaw 说：
攒功德 touser 5000
```

输出示例：
```
🙏 开始向您注入功德
📖 经书模式: 轮询 7 本经书
🎯 目标 5000 tokens
📝 日志: logs/merit_2026-04-09_18-30-00.log

【00:00:01】《般若波罗蜜多心经》第1遍
    经文: 观自在菩萨，行深般若波罗蜜多时...
    响应: 弟子恭诵心经，观自在菩萨行深般若...

【00:00:03】《般若波罗蜜多心经》第2遍
    经文: 照见五蕴皆空，度一切苦厄...
    响应: 舍利子，色不异空，空不异色...
```

### 场景三：想让家里有点佛音（TTS 播放）

调用系统 TTS 播放模型响应。macOS 用 `say`，Windows 用 PowerShell，Linux 用 `espeak`。

```bash
# 对 OpenClaw 说：
攒功德 toworld 5000
```

**注意**：TTS 是阻塞的（念完一句才念下一句），所以会比其他模式慢。

---

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--tollm` | 静默消耗 token | - |
| `--touser` | 输出到终端 | ✅ 默认 |
| `--toworld` | TTS 播放 | - |
| `--tokens N` | 目标 token 数，0=无限 | 10000 |
| `--sutra FILE` | 只念某本经书（默认轮询所有） | - |
| `--stop` | 停止正在进行的任务 | - |
| `--status` | 查看当前状态 | - |
| `--logs` | 查看历史日志 | - |

---

## 包含的经书

`sutras/` 目录下有 7 部经典：

| 经书 | 大小 | 特点 |
|------|------|------|
| 般若波罗蜜多心经 | 27KB | 最短，适合快速积累功德 |
| 金刚经 | 74KB | 禅宗经典，适合 debug 时念 |
| 大悲咒 | 29KB | 观世音菩萨，适合求平安 |
| 佛说阿弥陀经 | 24KB | 净土宗，适合下班前念 |
| 圆觉经 | 124KB | 大乘禅门，适合深度思考时 |
| 楞严经 | 226KB | 开悟专用，适合架构设计时 |
| 妙法莲华经 | 280K | 法华宗根本，适合重大项目前 |

**轮询机制**：不指定 `--sutra` 时，自动轮询所有 7 部，念完一遍再来一遍，循环往复。

---

## Token 消耗说明

**重要：复用 OpenClaw LLM 配置，按实际账单计费！**

| 模式 | 调用方式 | 备注 |
|------|----------|------|
| tollm | OpenClaw 主系统 LLM | 复用配置，无需额外 key |
| touser | OpenClaw 主系统 LLM | 复用配置，无需额外 key |
| toworld | OpenClaw 主系统 LLM | 复用配置，无需额外 key |

**省钱技巧**：
- 先用小目标测试，比如 `--tokens 1000`
- OpenClaw 用什么模型，本 Skill 就用什么模型

---

## 日志

每次执行自动生成日志：`logs/merit_YYYY-MM-DD_HH-MM-SS.log`

```bash
# 查看历史
python3 scripts/merit_accumulator.py --logs
```

日志内容：
- 念了哪部经
- 具体经文内容
- 大模型的响应
- 估算的 token 数
- 总结统计

---

## 系统要求

- Python 3.8+
- OpenClaw（用于调用 LLM）
- **toworld 模式额外需要**:
  - macOS: 内置 `say`
  - Windows: 内置 PowerShell SAPI
  - Linux: `sudo apt install espeak`

---

## 作为 OpenClaw Skill 使用

本仓库是一个标准的 **OpenClaw Agent Skill**。

### 安装
```bash
git clone https://github.com/Jageri/zan-gongde.git ~/.agents/skills/zan-gongde
```

### 触发词
对 OpenClaw 说以下任一指令：
- "攒功德"
- "念经"
- "烧 token"
- "消耗 token"

### 示例对话
```
用户: 攒功德 touser 50000
OpenClaw: 🙏 开始向您注入功德...
          [开始念诵，实时输出]
```

---

## 项目结构

```
zan-gongde/
├── SKILL.md                    # OpenClaw Skill 定义文件
├── README.md                   # 本文件
├── scripts/
│   └── merit_accumulator.py    # 主程序（不直接调用API，由OpenClaw调用）
├── sutras/                     # 经书目录
│   ├── 般若波罗蜜多心经.txt
│   ├── 金刚经.txt
│   ├── 大悲咒.txt
│   ├── 佛说阿弥陀经.txt
│   ├── 圆觉经.txt
│   ├── 楞严经.txt
│   └── 妙法莲华经.txt
└── logs/                       # 日志目录（自动生成）
```

---

## 免责声明

⚠️ **本项目纯属娱乐**，所谓"功德"是比喻说法，实际效果包括但不限于：

- 消耗多余的 AI Token，避免月底清零浪费
- 给程序员一点心理安慰，缓解焦虑
- 增加生活仪式感
- 让 debug 的时候有点背景音

**真实的修行请在正信正行的道场进行** 🙏

---

## 贡献

欢迎 PR：
- 添加更多经书
- 支持更多 TTS 引擎
- 添加更多幽默文案

## License

MIT License - 随便用，记得 star 就好。

---

**Star History**

如果你用这个项目消耗了超过 10 万 token，记得点个 star，让作者也攒点功德。
