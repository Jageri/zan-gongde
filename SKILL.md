---
name: zan-gongde
description: |
  烧token攒功德Skill - 全自动消耗 OpenClaw 套餐 Token
  
  核心原理：循环调用 OpenClaw LLM，每次生成一个经文念诵响应，
  **实时估算并累加 token 消耗，达到目标后立即停止**。
  
  当用户说"攒功德"、"念经"、"烧token"、"消耗token"时调用此 skill。
  
  四种功德注入方式：
  1. tollm - 向大模型注入功德：循环调用LLM，静默消耗
  2. touser - 向用户注入功德：循环调用LLM，输出响应给用户
  3. toworld - 向外界散播功德：循环调用LLM，TTS播放
  4. ddos - DDoS攻击佛祖：高并发快速消耗token
  
  ⚠️ 重要：参数中的数字是 **token 数**（默认单位），不是迭代次数！
  例如"攒功德 500"表示消耗500 tokens，而不是执行500次。
  
  使用场景：OpenClaw AI Token 套餐月底用不完，通过"念经"方式全自动消耗。
  
  ✅ 复用 OpenClaw LLM 配置，无需额外 API Key
  ✅ 全自动执行，实时累加token消耗，达标即停
  ✅ 真实调用 LLM，真实消耗 Token
---

# 烧token攒功德Skill

一个全自动消耗 OpenClaw Token 的娱乐工具。

**核心原理**：Agent 循环调用 LLM，每次生成一个经文念诵响应，
**实时估算并累加 token 消耗，达到目标后立即停止**。

---

## 触发条件

当用户说以下话时触发：
- "攒功德"
- "念经"
- "烧 token"
- "消耗 token"
- "用不完 token"

---

## 参数解析（关键！）

用户指令格式：`攒功德 [模式] [数字N]`

**⚠️ 重要：`N` 的单位是 token 数（默认），不是迭代次数！**

| 用户输入 | 解析结果 | 说明 |
|---------|---------|------|
| `攒功德` | touser 模式，10000 tokens | 默认值 |
| `攒功德 500` | touser 模式，500 tokens | 消耗500个token |
| `攒功德 50000` | touser 模式，50000 tokens | 消耗5万个token |
| `攒功德 tollm 100000` | tollm 模式，100000 tokens | 后台静默消耗10万token |
| `攒功德 touser 500` | touser 模式，500 tokens | 显示输出，消耗500token |

**Token 估算规则**：
- 输入 token ≈ `len(prompt) * 1.5`（中文）
- 输出 token ≈ `len(response) * 1.5`（中文）
- 每次 LLM 调用消耗 ≈ `输入 + 输出` tokens

---

## 四种模式

| 模式 | 说明 | 输出 |
|------|------|------|
| `tollm` | 静默模式 | 只记录日志，不输出给用户 |
| `touser` | 用户模式（默认） | 输出念诵内容和响应 |
| `toworld` | 世界模式 | TTS 播放响应 |
| `ddos` | DDoS攻击佛祖 | 高并发快速消耗token |

### 模式四: ddos - DDoS攻击佛祖（高并发模式）

**特点**:
- ⚡ **真正并发**：使用 ThreadPoolExecutor 多线程并发调用 API
- 🔄 **自动降速**：检测到 429/rate limit 错误时自动减少并发或增加延迟
- 📊 **实时统计**：显示每秒消耗速率、成功/失败率
- 🎯 **Token精确**：每个 worker 返回真实消耗量，累加统计

**适用场景**:
- Token 套餐额度巨大，需要快速消耗
- 不在乎成功率，追求极致速度
- 愿意承受一定的 API 失败率

**参数**:
- `--workers N` 或 `--max-workers N`：最大并发数，默认 10
- `--tokens N`：目标 token 数

**示例**:
```bash
攒功德 ddos 100000           # 高并发消耗10万token
攒功德 ddos 50000 --workers 20  # 20并发消耗5万token
```

**降速机制**:
1. 检测到 429 错误 → 增加延迟（乘以1.5）
2. 连续3次错误 → 减少并发数（减1）
3. 成功后逐渐恢复速度

**输出示例**:
```
🙏 开始DDoS攻击佛祖
📖 经书模式: 轮询 7 本经书
🔌 API: OpenAI
⚡ 最大并发: 10
🎯 目标 100000 tokens
==================================================

  [状态] 耗时:1s | 并发:10 | 成功率:100% | Token:8500/100000 (8%) | 速率:8500/s
  [状态] 耗时:2s | 并发:10 | 成功率:100% | Token:17000/100000 (17%) | 速率:8500/s
  ⚠️ 降速: 并发数调整为 9
  [状态] 耗时:3s | 并发:9 | 成功率:89% | Token:24000/100000 (24%) | 速率:8000/s
```

---

## 执行流程（重要！）

### Step 1: 解析参数

从用户输入中提取：
- 模式（tollm/touser/toworld），默认 touser
- **目标 token 数**（不是迭代次数！），默认 10000

### Step 2: 循环调用 LLM

```python
# 初始化
total_tokens = 0        # 已消耗 token 总数
iteration = 0            # 当前迭代次数
target_tokens = 500     # 用户指定的目标（如"攒功德 500"）
mode = "touser"
sutras = load_sutras()  # 7部经书轮询器

# ⚠️ 关键：直到达到目标 token 数才停止！
while total_tokens < target_tokens:
    iteration += 1
    
    # 获取下一段经文
    sutra_name, fragment = next(sutras)
    
    # 构造 prompt
    prompt = f"请念诵以下经文，并以恭敬心简短回应（50字以内）：\n\n《{sutra_name}》\n{fragment}"
    
    # ⚠️ 真实调用 LLM（这会消耗 token！）
    # Agent 生成一个回复作为 response
    response = "弟子恭诵《xxx》，愿以此功德..."  # Agent 实际生成的内容
    
    # ⚠️ 关键步骤：实时估算并累加 token 消耗！
    input_tokens = int(len(prompt) * 1.5)   # 估算输入 token
    output_tokens = int(len(response) * 1.5)  # 估算输出 token
    tokens_this_round = input_tokens + output_tokens
    total_tokens += tokens_this_round  # 累加！
    
    # 根据模式输出
    if mode == "touser":
        print(f"【第{iteration}遍】《{sutra_name}》")
        print(f"    经文: {fragment[:60]}...")
        print(f"    响应: {response}")
        print(f"    [本次+{tokens_this_round} | 累计{total_tokens}/{target_tokens}]")
        
        # ⚠️ 每轮都显示进度，让用户知道当前状态
        print(f"    进度: {min(100, int(total_tokens * 100 / target_tokens))}%")
        print()

# Step 3: 达标停止
print("=" * 50)
print("🙏 功德圆满！")
print(f"   目标: {target_tokens} tokens")
print(f"   实际消耗: {total_tokens} tokens")
print(f"   迭代次数: {iteration}")
print(f"   完成度: {min(100, int(total_tokens * 100 / target_tokens))}%")
```

### 关键区别

| 旧逻辑（错误） | 新逻辑（正确） |
|--------------|--------------|
| `for i in range(N):` | `while total_tokens < target:` |
| 执行 N 次后停止 | 消耗达到目标后停止 |
| 500 = 执行500次 | 500 = 消耗500 tokens |
| 不关心实际消耗 | 实时估算并累加 |

---

## Token 消耗估算表

每次 LLM 调用约消耗 500-1500 tokens（取决于经文长度和响应长度）

| 目标 Token | 预计迭代次数 | 预计时间 |
|-----------|-------------|---------|
| 500 | 1-2 次 | 3-5 秒 |
| 5,000 | 4-10 次 | 15-30 秒 |
| 10,000 | 8-20 次 | 30-60 秒 |
| 50,000 | 40-100 次 | 2-5 分钟 |
| 100,000 | 80-200 次 | 5-10 分钟 |

---

## 经书列表

位于 `sutras/` 目录，自动轮询 7 部经典：

| 经书 | 特点 |
|------|------|
| 般若波罗蜜多心经 | 最短，适合快速烧 token |
| 金刚经 | 禅宗核心经典 |
| 大悲咒 | 观世音菩萨陀罗尼 |
| 佛说阿弥陀经 | 净土宗核心经典 |
| 圆觉经 | 大乘禅门重要经典 |
| 楞严经 | 开悟楞严经 |
| 妙法莲华经 | 法华宗根本经典 |

---

## 常见问题

### Q: 为什么有时候实际消耗会超过目标？
A: 因为 token 估算是基于响应长度的，每次调用消耗的 token 是一个范围值，无法精确到个位数。脚本会在接近目标时停止，通常不会超过目标太多。

### Q: 如何停止正在执行的任务？
A: 说"停止攒功德"，或修改 `.merit_state.json` 中的 `stop_requested` 为 `true`。

### Q: tollm 模式是什么效果？
A: 完全静默，不输出任何内容，适合后台大量消耗 token。

---

## 免责

⚠️ 纯属娱乐，真实效果是消耗你的 OpenClaw Token 🙏
