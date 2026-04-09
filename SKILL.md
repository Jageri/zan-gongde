---
name: zan-gongde
description: |
  烧token攒功德Skill - OpenClaw Agent Skill，用于通过真实调用大模型API消耗多余的 AI Token。
  
  核心原则：所有三种模式(tollm/touser/toworld)都真实调用 OpenAI/Anthropic API，区别仅在于输出方式不同。
  
  当用户说"攒功德"、"念经"、"烧token"、"消耗token"时调用此 skill。
  
  三种功德注入方式：
  1. tollm - 向大模型注入功德：真实调用API，静默消耗token，不打扰用户
  2. touser - 向用户注入功德：真实调用API，输出响应给用户阅读
  3. toworld - 向外界散播功德：真实调用API，TTS播放模型响应
  
  使用场景：AI 套餐 token 用不完时，通过"念经"方式消耗 token。
  
  注意：所有模式都需要配置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY！
---

# 烧token攒功德Skill

一个 OpenClaw Agent Skill，用于在 AI Token 过剩时通过真实调用大模型API、念诵佛经的方式消耗 token。

**核心原则：所有三种模式(tollm/touser/toworld)都真实调用 OpenAI/Anthropic API，区别仅在于输出方式不同。**

## 触发条件

当用户表达以下意图时调用此 skill：
- "攒功德"
- "念经"
- "烧 token"
- "消耗 token"
- "用不完 token"

## 三种模式详解

### 模式一: tollm - 向大模型注入功德（完全静默）

**特点**:
- ✅ 真实调用 OpenAI/Anthropic API
- ✅ 完全静默，用户不会收到任何消息
- ✅ 输入+输出都消耗 token，最大化烧 token
- ✅ 适合后台静默消耗

**执行逻辑**:
1. 构造经文 prompt
2. **真实调用大模型API**，获取响应
3. 不向用户展示任何内容（静默执行）
4. 自动记录日志

**API配置**:
- 需设置环境变量 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`
- 所有三种模式都需要此配置

**调用方式**:
```python
# 用户说: "攒功德 tollm 100000"
exec(command="python3 scripts/merit_accumulator.py --tollm --tokens 100000 --quiet")

# 返回给用户: "已开始后台静默注入功德，目标10万tokens..."
```

---

### 模式二: touser - 向用户注入功德

**特点**:
- 📱 真实调用 API，响应通过 OpenClaw 发送给用户
- 📊 实时显示念诵进度（按真实token统计）
- 🎨 格式化输出，有仪式感
- 📝 自动记录日志

**执行逻辑**:
1. 构造经文 prompt
2. **真实调用大模型API**，获取响应
3. 逐段输出经文和模型响应（通过 OpenClaw 发送）
4. 显示时间戳、遍数、token统计
5. 记录日志

**注意**：同样需要 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`

**输出示例**:
```
🙏 开始向您注入功德
📖 经书模式: 轮询 7 本经书
🎯 目标 100000 tokens
📝 日志: logs/merit_2025-01-01_12-00-00.log
==================================================

【00:00:01】《般若波罗蜜多心经》第1遍
    观自在菩萨，行深般若波罗蜜多时...

【00:00:03】《般若波罗蜜多心经》第2遍
    照见五蕴皆空，度一切苦厄...

📖 切换至《金刚经》

【00:01:15】《金刚经》第25遍
    如是我闻，一时佛在舍卫国祇树给孤独园...

  ... 已念诵 100 遍, 累计 15000 字, 22500/100000 tokens ...
```

**调用方式**:
```python
# 用户说: "攒功德" 或 "攒功德 touser 100000"
exec(command="python3 scripts/merit_accumulator.py --touser --tokens 100000")

# 脚本输出会直接返回给用户
```

---

### 模式三: toworld - 向外界散播功德（TTS）

**特点**:
- 🔊 真实调用 API，TTS 播放模型响应
- 🖥️ 自动检测操作系统
- 📢 让功德通过声音传播
- 📝 自动记录日志

**系统支持**:

| 系统 | TTS 工具 | 说明 |
|------|----------|------|
| macOS | `say` | 内置，无需安装 |
| Windows | PowerShell SAPI | 内置，无需安装 |
| Linux | `espeak`/`festival` | 可能需要手动安装 |

**执行逻辑**:
1. 构造经文 prompt
2. **真实调用大模型API**，获取响应
3. 调用系统 TTS 播放模型响应（阻塞等待）
4. 每20遍自动回向
5. 记录日志

**注意**：同样需要 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`，加上 TTS 工具

**调用方式**:
```python
# 用户说: "攒功德 toworld 50000"
exec(command="python3 scripts/merit_accumulator.py --toworld --tokens 50000")

# 返回给用户: "开始向外界散播功德，目标5万tokens..."
```

---

## 使用方式

### 参数格式

用户指令格式：`攒功德 [模式] [token数]`

- **模式**：`tollm` | `touser` | `toworld`
  - 不传默认 `touser`

- **Token数**：整数
  - `0` 表示无限模式（直到上限或手动停止）
  - 不传默认 10000 token

### 指令对照表

| 用户说的话 | 模式 | Token数 | 执行脚本 |
|-----------|------|---------|---------|
| "攒功德" | touser | 10000 | `--touser --tokens 10000` |
| "攒功德 50000" | touser | 50000 | `--touser --tokens 50000` |
| "攒功德 touser 100000" | touser | 100000 | `--touser --tokens 100000` |
| "攒功德 tollm 0" | tollm | 无限 | `--tollm --tokens 0 --quiet` |
| "攒功德 toworld 50000" | toworld | 50000 | `--toworld --tokens 50000` |
| "停止攒功德" | - | - | `--stop` |
| "查看攒功德状态" | - | - | `--status` |
| "查看攒功德日志" | - | - | `--logs` |

---

## 执行流程

### Step 1: 解析用户指令

从用户输入中提取：
1. 模式（tollm/touser/toworld）- 默认 touser
2. Token数 - 默认 10000，0 表示无限
3. 经书（可选）- 轮询所有或指定单本

### Step 2: 调用脚本

使用 `exec` 执行主脚本：

```python
# 示例: 用户说 "攒功德 touser 100000"
exec(command="python3 scripts/merit_accumulator.py --touser --tokens 100000")
```

### Step 3: 处理输出

| 模式 | 处理方式 |
|------|----------|
| tollm | 静默执行，只返回开始/结束提示，生成日志 |
| touser | 将脚本 stdout 直接返回给用户，生成日志 |
| toworld | 返回开始提示，TTS 播放，生成日志 |

---

## 经书资源

可用经书位于 `sutras/` 目录：

| 经书 | 大小 | 说明 |
|------|------|------|
| 般若波罗蜜多心经.txt | 27K | 最简短精髓的般若经典 |
| 金刚经.txt | 74K | 禅宗核心经典 |
| 大悲咒.txt | 29K | 观世音菩萨陀罗尼 |
| 佛说阿弥陀经.txt | 24K | 净土宗核心经典 |
| 圆觉经.txt | 124K | 大乘禅门重要经典 |
| 楞严经.txt | 226K | 开悟楞严经 |
| 妙法莲华经.txt | 280K | 法华宗根本经典 |

**轮询所有经书**（默认）：不指定 `--sutra` 时，自动轮询所有7部经书，循环往复

**指定单本经书**：
```python
exec(command="python3 scripts/merit_accumulator.py --touser --tokens 10000 --sutra 金刚经.txt")
```

---

## Token 消耗估算

| 模式 | 消耗方式 | 估算 |
|------|----------|------|
| tollm | 输入+输出 token | 约 3 token/汉字 |
| touser | 输入+输出 token | 约 1.5 token/汉字 |
| toworld | 输入+输出 token | 约 1.5 token/汉字 |

念诵1万字 ≈ 消耗1.5万 token (touser/toworld)
念诵1万字 ≈ 消耗3万 token (tollm，双倍消耗)

---

## 日志记录

每次执行自动生成日志文件：`logs/merit_YYYY-MM-DD_HH-MM-SS.log`

日志内容：
- 执行时间
- 每段念诵的经文内容
- 消耗的 token 数
- 总结统计

查看历史日志：
```python
exec(command="python3 scripts/merit_accumulator.py --logs")
```

---

## 状态管理

脚本自动维护状态文件 `.merit_state.json`：
- 记录当前模式、经书、进度
- 支持 `--stop` 命令中断
- 支持 `--status` 查询状态

---

## 完整调用示例

### 场景1: 用户说"攒功德"

```python
# 默认 touser 模式，10000 tokens
exec(command="python3 scripts/merit_accumulator.py --touser --tokens 10000")

# 将脚本输出返回给用户
```

### 场景2: 用户说"攒功德 tollm 0"

```python
# 后台无限注入（完全静默）
exec(command="python3 scripts/merit_accumulator.py --tollm --tokens 0 --quiet")

# 返回: "已开始后台静默注入功德，将持续直到token上限..."
```

### 场景3: 用户说"攒功德 toworld 50000"

```python
# TTS 播放直到5万tokens
exec(command="python3 scripts/merit_accumulator.py --toworld --tokens 50000")

# 返回: "开始向外界散播功德，目标5万tokens..."
```

### 场景4: 用户说"停止"

```python
exec(command="python3 scripts/merit_accumulator.py --stop")
```

---

## 注意事项

1. **tollm 模式**：完全静默，不会打扰用户，但会持续消耗 token
2. **toworld 模式**：需要系统支持 TTS，不支持时会降级为文本输出
3. **tokens=0**：无限模式，必须通过 `--stop` 停止
4. **状态文件**：位于 skill 根目录，名为 `.merit_state.json`
5. **日志文件**：位于 `logs/` 目录，按时间命名

---

## TTS 支持详情

### macOS
使用内置 `say` 命令：
```bash
say "南无阿弥陀佛"
```

### Windows
使用 PowerShell SAPI：
```powershell
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak("南无阿弥陀佛")
```

### Linux
尝试以下工具（按优先级）：
- `spd-say` (speech-dispatcher)
- `espeak`
- `festival`

---

## 免责与趣味声明

⚠️ **本 skill 纯属娱乐**，所谓"功德"是比喻说法，实际效果包括但不限于：
- 消耗多余的 AI Token
- 给用户一点心理安慰
- 增加一点生活仪式感
- 让程序员在 debug 时有点精神寄托

**真实的修行请在正信正行的道场进行** 🙏
