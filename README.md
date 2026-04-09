# 攒功德 (Zan Gongde) 🙏

> **Coding 套餐月底 token 没花完？攒功德了解一下。**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 这是什么神仙项目？

想象一下这个场景：

> 月底了，你的 OpenAI API 额度还有 50 万 token 没用完。不用完就清零，用又不知道用去哪。焦虑，彷徨，心痛。

这时候你需要 **攒功德**。

这个项目让你可以通过念诵佛经的方式，**理直气壮地消耗 token**。三种功德注入渠道，任君选择：

| 模式 | 功德去向 | 适合人群 |
|------|---------|---------|
| **tollm** | 真实调用 OpenAI/Anthropic API | 土豪、Token 多到没处花 |
| **touser** | 输出到终端给自己看 | 想静静、需要心理安慰 |
| **toworld** | 系统 TTS 播放出来 | 有音响、想营造仪式感 |

**核心卖点**：
- ✅ 真实消耗 token（不是虚拟统计）
- ✅ 附带经书轮询，念完一本自动下一本
- ✅ 自动记录日志，月底可以发朋友圈炫耀
- ✅ 支持 macOS / Windows / Linux

## 安装

```bash
git clone https://github.com/Jageri/zan-gongde.git
cd zan-gongde
```

不需要 `pip install`，开箱即用（tollm 模式除外，那个需要装 openai/anthropic 库）。

## 快速开始

### 场景一：Token 太多，想真实烧掉

适合月底还剩几万 token 没花完的同学。

```bash
# 配置 API Key
export OPENAI_API_KEY="sk-你的key"

# 开始烧 token，目标 10 万
python3 scripts/merit_accumulator.py --tollm --tokens 100000
```

然后你就可以去泡杯茶了。脚本会真实调用 GPT-3.5-turbo，念诵经文，消耗 token。

### 场景二：只是想静静

不需要 API Key，输出经文到终端，给自己一点心理安慰。

```bash
python3 scripts/merit_accumulator.py --touser --tokens 5000
```

输出示例：
```
🙏 开始向您注入功德
📖 经书模式: 轮询 7 本经书
🎯 目标 5000 tokens
📝 日志: logs/merit_2026-04-09_18-30-00.log

【00:00:01】《般若波罗蜜多心经》第1遍
    观自在菩萨，行深般若波罗蜜多时...

【00:00:03】《般若波罗蜜多心经》第2遍
    照见五蕴皆空，度一切苦厄...

📖 切换至《金刚经》

【00:01:15】《金刚经》第25遍
    如是我闻，一时佛在舍卫国祇树给孤独园...
```

### 场景三：想让家里有点佛音

调用系统 TTS 播放经文。macOS 用 `say`，Windows 用 PowerShell，Linux 用 `espeak`。

```bash
python3 scripts/merit_accumulator.py --toworld --tokens 5000
```

**注意**：TTS 是阻塞的（念完一句才念下一句），所以会比其他模式慢。适合挂机。

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--tollm` | 真实调用 API，最大化烧 token | - |
| `--touser` | 输出到终端 | ✅ 默认 |
| `--toworld` | TTS 播放 | - |
| `--tokens N` | 目标 token 数，0=无限 | 10000 |
| `--sutra FILE` | 只念某本经书（默认轮询所有） | - |
| `--stop` | 停止正在进行的任务 | - |
| `--status` | 查看当前状态 | - |
| `--logs` | 查看历史日志 | - |

## 包含的经书

` 目录下有 7 部经典：

| 经书 | 大小 | 特点 |
|------|------|------|
| 般若波罗蜜多心经 | 27KB | 最短，适合快速积累功德 |
| 金刚经 | 74KB | 禅宗经典，适合 debug 时念 |
| 大悲咒 | 29KB | 观世音菩萨，适合求平安 |
| 佛说阿弥陀经 | 24KB | 净土宗，适合下班前念 |
| 圆觉经 | 124KB | 大乘禅门，适合深度思考时 |
| 楞严经 | 226KB | 开悟专用，适合架构设计时 |
| 妙法莲华经 | 280KB | 法华宗根本，适合重大项目前 |

**轮询机制**：不指定 `--sutra` 时，自动轮询所有 7 部，念完一遍再来一遍，循环往复。

## Token 消耗估算

| 模式 | 消耗方式 | 备注 |
|------|----------|------|
| tollm | 真实 API 调用 | 以实际账单为准，一般 3-5 tokens/汉字 |
| touser | 估算 | ~2 tokens/汉字 |
| toworld | 估算 | ~2 tokens/汉字 |

**省钱技巧**：
- tollm 模式用 GPT-3.5-turbo（便宜）
- 目标别设太大，先试试 1000 tokens

## 日志

每次执行自动生成日志：`logs/merit_YYYY-MM-DD_HH-MM-SS.log`

```bash
# 查看历史
python3 scripts/merit_accumulator.py --logs
```

日志里会记录：
- 念了哪部经
- 具体经文内容
- 消耗的 token 数
- 总结统计

## 系统要求

- Python 3.8+
- **tollm 模式**: `pip install openai` 或 `pip install anthropic`
- **toworld 模式**:
  - macOS: 内置 `say`
  - Windows: 内置 PowerShell SAPI
  - Linux: `sudo apt install espeak`

## 作为 OpenClaw Skill 使用

如果你用 [OpenClaw](https://github.com/openclaw/openclaw)，可以直接当 Skill 用：

1. 克隆到 `~/.agents/skills/zan-gongde`
2. 说"攒功德"即可触发

触发词：攒功德、念经、烧 token、消耗 token

## 免责声明

⚠️ **本项目纯属娱乐**，所谓"功德"是比喻说法，实际效果包括但不限于：

- 消耗多余的 AI Token，避免月底清零浪费
- 给程序员一点心理安慰，缓解焦虑
- 增加生活仪式感
- 让 debug 的时候有点背景音

**真实的修行请在正信正行的道场进行** 🙏

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
